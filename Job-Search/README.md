# 🔎 Job Search with freehire

Search **3.3M+ live IT job postings** pulled straight from company career pages, using the free, keyless API of [freehire](https://github.com/strelov1/freehire) ([freehire.me](https://freehire.me)).

`freehire_jobs.py` is a single Python script using only the standard library, so there's nothing to install. It can:

- **search** postings with free text plus filters (location, remote/hybrid, seniority, skills, salary, recency…)
- **facets**: count how many postings match each filter value (e.g. which cities or skills come up most)
- **job**: show one posting in detail
- export results to **CSV** (opens in Excel, Tableau or Power BI) or raw **JSON**

## Quick start

```bash
cd Job-Search

# Data Analyst jobs in Dallas
python freehire_jobs.py search "data analyst" --cities Dallas

# Remote US analyst roles posted in the last 14 days, title match only, newest first
python freehire_jobs.py search "data analyst" --title-only --countries US \
    --work-mode remote --posted-within 14 --sort posted_at

# Roles that need SQL *and* Tableau, entry/mid level, $70k+, saved to CSV
python freehire_jobs.py search "analyst" --countries US --skills sql,tableau --skills-all \
    --seniority junior,middle --salary-min 70000 --max 300 --csv analyst_jobs.csv

# Every data-analytics posting in Texas cities, with full descriptions
python freehire_jobs.py search --category data_analytics --cities Dallas,Austin,Houston \
    --descriptions --max 500 --csv texas_data_jobs.csv -q

# Market view: which cities, skills and seniority levels dominate?
python freehire_jobs.py facets "data analyst" --countries US --only cities,skills,seniority

# One posting
python freehire_jobs.py job <public_slug>
```

Each result shows the title, company, location, work mode, salary (when listed), posting date and the **direct link to the company's own application page**.

## Filters

| Flag | Values |
| --- | --- |
| `"query"` | Free text over title, company, description and location. Supports `"quoted words"`, `-exclude` and `OR` |
| `--title-only` | Match the query against job titles only (fewer false positives) |
| `--countries` | ISO codes: `US`, `CA`, `GB`… |
| `--cities` | `Dallas,Austin`… |
| `--regions` | `north_america`, `eu`, `uk`, `latam`, `apac`, `global`… |
| `--work-mode` | `remote`, `hybrid`, `onsite` |
| `--category` | `data_analytics`, `business_analysis`, `data_science`, `data_engineering`, `marketing`… |
| `--seniority` / `--exclude-seniority` | `intern`, `junior`, `middle`, `senior`, `lead`, `staff`, `principal`, `c_level` |
| `--skills` (+ `--skills-all`) | `sql,python,tableau,power-bi`… (any by default, all with `--skills-all`) |
| `--employment-type` | `full_time`, `part_time`, `contract`, `internship` |
| `--salary-min` + `--currency` | e.g. `--salary-min 80000 --currency USD` |
| `--posted-within DAYS` | Only recent postings |
| `--visa` | Only roles offering visa sponsorship |
| `--no-clearance` | Hide roles requiring a security clearance |
| `--domains`, `--company-type`, `--collections`, `--company-slug` | Industry, company kind, lists like `fortune500` / `us-h1b-sponsor`, specific companies |
| `--param KEY=VALUE` | Any other API filter, e.g. `--param company_size=1000+` |

Comma-separated values are ORed. Location filters (`--countries`, `--cities`, `--regions`) widen each other, so for one city pass just `--cities`. If the API ignores a filter (for example a typo), the script prints a warning instead of quietly returning broader results.

Output options for `search`: `--max N` (default 25, up to 10,000; pages automatically), `--sort posted_at|salary_min|…`, `--csv FILE`, `--json FILE`, `--descriptions`, `-q` (no table).

## Notes

- **No key needed.** The public API is rate-limited per IP for personal, non-commercial use; the script waits and retries on `429`. If you have a freehire API plan, set `FREEHIRE_API_KEY` to use it.
- `FREEHIRE_API_URL` points the script at a self-hosted freehire instance (default `https://freehire.me/api/v1`).
- Full API reference: [freehire.me/docs/api](https://freehire.me/docs/api). freehire also ships an official [CLI](https://github.com/strelov1/freehire-cli) and an [MCP server](https://github.com/strelov1/freehire-mcp) for Claude.
- Job data © freehire and the source companies, used under the [freehire data licence](https://freehire.me/terms#data-licence).
