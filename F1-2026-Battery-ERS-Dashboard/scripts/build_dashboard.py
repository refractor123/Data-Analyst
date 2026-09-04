"""Inject the aggregated JSON into the HTML template -> standalone dashboard.html."""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
data = (BASE / "data" / "dashboard_data.json").read_text()
tpl = (BASE / "scripts" / "dashboard_template.html").read_text()
html = tpl.replace("/*__DATA__*/null", json.dumps(json.loads(data)))
out = BASE / "dashboard.html"
out.write_text(html)
print("Wrote", out, f"({len(html):,} bytes)")
