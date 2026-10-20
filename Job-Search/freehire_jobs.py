#!/usr/bin/env python3
"""Search live job postings from freehire (https://freehire.me).

freehire aggregates millions of open IT postings straight from company career
pages and serves them through a public, keyless API. This script wraps the
endpoints that matter for a job search:

    search  - full-text + faceted search      (GET /jobs/search)
    facets  - counts per filter value          (GET /jobs/facets)
    job     - one posting by its public slug   (GET /jobs/{slug})

Standard library only - no pip install needed.

Examples:
    python freehire_jobs.py search "data analyst" --cities Dallas
    python freehire_jobs.py search "data analyst" --title-only --work-mode remote \
        --countries US --skills sql,tableau --max 200 --csv data_analyst_jobs.csv
    python freehire_jobs.py facets "data analyst" --countries US
    python freehire_jobs.py job <public_slug>

API reference: https://freehire.me/docs/api
"""

import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = os.environ.get("FREEHIRE_API_URL", "https://freehire.me/api/v1")
API_KEY = os.environ.get("FREEHIRE_API_KEY")  # optional; only raises rate limits
USER_AGENT = "Data-Analyst-portfolio-job-search/1.0"
PAGE_SIZE = 100            # API max per request
MAX_DEPTH = 10000          # API refuses offset + limit beyond this

CSV_FIELDS = [
    "title", "company", "location", "work_mode", "seniority", "category",
    "employment_type", "salary_min", "salary_max", "salary_currency",
    "salary_period", "skills", "posted_at", "reality", "url", "freehire_url",
    "public_slug",
]

# CLI flag -> API filter param. Each accepts a comma-separated list (ORed).
FACET_FLAGS = {
    "category": "Specialization, e.g. data_analytics,business_analysis,data_science",
    "seniority": "intern, junior, middle, senior, lead, staff, principal, c_level",
    "work_mode": "remote, hybrid, onsite",
    "countries": "ISO country codes, e.g. US,CA",
    "cities": "City names, e.g. Dallas,Austin",
    "regions": "global, north_america, latam, eu, uk, mena, africa, apac, cis",
    "skills": "e.g. sql,python,tableau (add --skills-all to require every one)",
    "employment_type": "full_time, part_time, contract, internship, fellowship",
    "company_type": "product, startup, outsource, outstaff, agency, inhouse, government",
    "domains": "Industry, e.g. fintech,healthcare,ecommerce",
    "collections": "e.g. fortune500,bigtech,us-h1b-sponsor",
    "company_slug": "Only these companies (freehire company slugs)",
}


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def api_get(path, params=None, retries=3):
    """GET a freehire endpoint and return the decoded JSON body."""
    query = urllib.parse.urlencode(
        {k: v for k, v in (params or {}).items() if v is not None and v != ""}
    )
    url = f"{BASE_URL}{path}" + (f"?{query}" if query else "")
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as err:
            if err.code in (429, 503) and attempt < retries:
                wait = int(err.headers.get("Retry-After") or 2 ** (attempt + 1))
                print(f"  rate limited / busy ({err.code}), retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            try:
                message = json.load(err).get("error", err.reason)
            except (ValueError, AttributeError):
                message = err.reason
            sys.exit(f"freehire API error {err.code}: {message}\n  {url}")
        except (urllib.error.URLError, OSError) as err:
            sys.exit(f"Could not reach freehire ({getattr(err, 'reason', err)}).\n  {url}")


def warn_ignored(meta):
    """freehire silently drops unknown filters - surface them so results aren't misread."""
    for item in (meta or {}).get("ignored_params") or []:
        if isinstance(item, dict):
            hint = f" (did you mean '{item['did_you_mean']}'?)" if item.get("did_you_mean") else ""
            name = item.get("param") or item.get("name") or item
        else:
            name, hint = item, ""
        print(f"warning: filter '{name}' was ignored by the API{hint}", file=sys.stderr)


# --------------------------------------------------------------------------- #
# Query building
# --------------------------------------------------------------------------- #
def build_filters(args):
    params = {"q": args.query or None}
    if args.title_only:
        params["q_fields"] = "title"
    for flag in FACET_FLAGS:
        value = getattr(args, flag)
        if value:
            params[flag] = value
    if args.skills_all:
        params["skills_mode"] = "and"
    if args.exclude_seniority:
        params["seniority_exclude"] = args.exclude_seniority
    if args.salary_min:
        params["salary_min"] = args.salary_min
        params["salary_currency"] = args.currency
    if args.posted_within:
        params["posted_within_days"] = args.posted_within
    if args.visa:
        params["visa_sponsorship"] = "true"
    if args.no_clearance:
        params["requires_clearance"] = "false"
    for raw in args.param or []:
        key, sep, value = raw.partition("=")
        if not sep:
            sys.exit(f"--param expects key=value, got '{raw}'")
        params[key] = value
    return params


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #
def flatten(job):
    enr = job.get("enrichment") or {}
    reality = job.get("reality") or {}
    return {
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "work_mode": job.get("work_mode"),
        "seniority": enr.get("seniority"),
        "category": enr.get("category"),
        "employment_type": enr.get("employment_type"),
        "salary_min": enr.get("salary_min"),
        "salary_max": enr.get("salary_max"),
        "salary_currency": enr.get("salary_currency"),
        "salary_period": enr.get("salary_period"),
        "skills": ", ".join(job.get("skills") or []),
        "posted_at": (job.get("posted_at") or job.get("created_at") or "")[:10],
        "reality": reality.get("class"),
        "url": job.get("url") or job.get("apply_url"),
        "freehire_url": f"https://freehire.me/jobs/{job.get('public_slug')}",
        "public_slug": job.get("public_slug"),
    }


def fmt_salary(row):
    lo, hi = row["salary_min"], row["salary_max"]
    if not lo and not hi:
        return ""
    k = lambda n: f"{n / 1000:.0f}k" if n and n >= 1000 else str(n or "?")
    span = k(lo) if lo == hi or not hi else f"{k(lo)}-{k(hi)}"
    return f"{span} {row['salary_currency'] or ''}".strip()


def clip(text, width):
    text = str(text or "")
    return text if len(text) <= width else text[: width - 1] + "…"


def print_table(rows, total):
    print(f"\n{total:,} matching postings - showing {len(rows)}\n")
    header = f"{'#':>3}  {'Title':<40} {'Company':<22} {'Location':<24} {'Mode':<7} {'Salary':<16} {'Posted':<10}"
    print(header)
    print("-" * len(header))
    for i, r in enumerate(rows, 1):
        print(
            f"{i:>3}  {clip(r['title'], 40):<40} {clip(r['company'], 22):<22} "
            f"{clip(r['location'], 24):<24} {clip(r['work_mode'], 7):<7} "
            f"{clip(fmt_salary(r), 16):<16} {r['posted_at']:<10}"
        )
        print(f"     {r['url'] or r['freehire_url']}")
    print()


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_search(args):
    params = build_filters(args)
    if args.sort:
        params["sort"], params["order"] = args.sort, args.order
    path = "/agent/jobs/search" if args.descriptions else "/jobs/search"
    if args.descriptions:
        params["description_format"] = "text"

    wanted = min(args.max, MAX_DEPTH)
    jobs, total, offset = [], 0, 0
    while len(jobs) < wanted:
        limit = min(PAGE_SIZE, wanted - len(jobs))
        body = api_get(path, {**params, "limit": limit, "offset": offset})
        meta = body.get("meta") or {}
        if offset == 0:
            warn_ignored(meta)
        page = body.get("data") or []
        total = meta.get("total", len(page))
        jobs.extend(page)
        offset += len(page)
        if len(page) < limit or offset >= total:
            break

    rows = [flatten(j) for j in jobs]
    if args.descriptions:
        for row, job in zip(rows, jobs):
            row["description"] = job.get("description")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(jobs, fh, indent=2, ensure_ascii=False)
        print(f"Saved {len(jobs)} raw postings to {args.json}", file=sys.stderr)
    if args.csv:
        fields = CSV_FIELDS + (["description"] if args.descriptions else [])
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved {len(rows)} postings to {args.csv}", file=sys.stderr)
    if not args.quiet:
        print_table(rows, total)


def cmd_facets(args):
    params = build_filters(args)
    # /jobs/facets doesn't read q_fields; express title-only with the title: operator instead
    if params.pop("q_fields", None) and params.get("q"):
        params["q"] = f'title:"{params["q"]}"'
    body = api_get("/jobs/facets", params)
    warn_ignored(body.get("meta"))
    data = body.get("data") or {}
    print(f"\n{data.get('total', 0):,} matching postings\n")
    facets = data.get("facets") or {}
    for name in args.only.split(",") if args.only else sorted(facets):
        counts = facets.get(name) or {}
        if not counts:
            continue
        print(f"{name}:")
        for value, n in sorted(counts.items(), key=lambda kv: -kv[1])[: args.top]:
            print(f"  {value:<32} {n:>9,}")
        print()
    for name, s in (data.get("stats") or {}).items():
        print(f"{name}: min {s.get('min')}  max {s.get('max')}")


def cmd_job(args):
    job = api_get(f"/jobs/{urllib.parse.quote(args.slug)}").get("data") or {}
    if args.json:
        print(json.dumps(job, indent=2, ensure_ascii=False))
        return
    row = flatten(job)
    for key in CSV_FIELDS:
        if row.get(key):
            print(f"{key:<16} {row[key]}")
    if job.get("closed_at"):
        print(f"{'closed_at':<16} {job['closed_at']}")
    summary = (job.get("enrichment") or {}).get("summary")
    if summary:
        print(f"\n{summary}")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def add_filter_args(p):
    p.add_argument("query", nargs="?", help='Full-text query, e.g. "data analyst"')
    p.add_argument("--title-only", action="store_true", help="Match the query against job titles only")
    for flag, help_text in FACET_FLAGS.items():
        p.add_argument(f"--{flag.replace('_', '-')}", dest=flag, help=help_text)
    p.add_argument("--skills-all", action="store_true", help="Require every listed skill (default: any)")
    p.add_argument("--exclude-seniority", help="Drop these levels, e.g. senior,lead,staff")
    p.add_argument("--salary-min", type=int, help="Minimum salary (with --currency)")
    p.add_argument("--currency", default="USD", help="Salary currency: USD, EUR, GBP, RUB (default USD)")
    p.add_argument("--posted-within", type=int, metavar="DAYS", help="Only postings from the last N days")
    p.add_argument("--visa", action="store_true", help="Only jobs offering visa sponsorship")
    p.add_argument("--no-clearance", action="store_true", help="Exclude jobs requiring a security clearance")
    p.add_argument("--param", action="append", metavar="KEY=VALUE",
                   help="Any other API filter, e.g. --param company_size=1000+ (repeatable)")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Search live job postings on freehire.me")
    sub = parser.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="Search job postings")
    add_filter_args(s)
    s.add_argument("--max", type=int, default=25, help="Max postings to fetch (default 25, up to 10000)")
    s.add_argument("--sort", choices=["posted_at", "created_at", "salary_min", "salary_max", "view_count"],
                   help="Sort field (default: relevance, or newest without a query)")
    s.add_argument("--order", choices=["desc", "asc"], default="desc")
    s.add_argument("--descriptions", action="store_true", help="Include full job descriptions (plain text)")
    s.add_argument("--csv", metavar="FILE", help="Save results to a CSV file")
    s.add_argument("--json", metavar="FILE", help="Save raw API results to a JSON file")
    s.add_argument("-q", "--quiet", action="store_true", help="Don't print the results table")
    s.set_defaults(func=cmd_search)

    f = sub.add_parser("facets", help="Count matching postings per filter value")
    add_filter_args(f)
    f.add_argument("--only", help="Comma-separated facets to show, e.g. seniority,skills,cities")
    f.add_argument("--top", type=int, default=15, help="Values to show per facet (default 15)")
    f.set_defaults(func=cmd_facets)

    j = sub.add_parser("job", help="Show one posting by its public slug")
    j.add_argument("slug")
    j.add_argument("--json", action="store_true", help="Print the raw JSON")
    j.set_defaults(func=cmd_job)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
