# [H] PraisonAI: SQL Injection via unvalidated `table_prefix` in 9 conversation store backends (incomplete fix for CVE-2026-40315)

## Summary
Severity: High
Advisory: GHSA-rg3h-x3jw-7jm5
CVE: CVE-2026-41496
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-17
Source: https://github.com/advisories/GHSA-rg3h-x3jw-7jm5
Type: github-advisory

## Affected
- PyPI: `praisonai` — affected >=0 <4.5.149
- PyPI: `praisonaiagents` — affected >=0 <1.6.8

## Details
The fix for [CVE-2026-40315](https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-x783-xp3g-mqhp) added input validation to `SQLiteConversationStore` only. Nine sibling backends — MySQL, PostgreSQL, async SQLite/MySQL/PostgreSQL, Turso, SingleStore, Supabase, SurrealDB — pass `table_prefix` straight into f-string SQL. Same root cause, same code pattern, same exploitation. 52 unvalidated injection points across the codebase.

`postgres.py` additionally accepts an unvalidated `schema` parameter used directly in DDL.

### Severity

**High** — CWE-89 (SQL Injection)

CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N — **8.1**

Exploitable in any deployment where `table_prefix` is derived from external input (multi-tenant setups, API-driven configuration, user-modifiable config files). Default config (`"praison_"`) is not affected.

### Details

The [CVE-2026-40315 fix](https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-x783-xp3g-mqhp) added this guard to `sqlite.py:52`:

```python
# sqlite.py — PATCHED
import re
if not re.match(r'^[a-zA-Z0-9_]*$', table_prefix):
    raise ValueError("table_prefix must contain only alphanumeric characters and underscores")
```

The following backends perform the identical `table_prefix → f-string SQL` pattern **without this guard**:

| Backend          | File                                         | Line            | Injection points        |
| ---------------- | -------------------------------------------- | --------------- | ----------------------- |
| MySQL            | `persistence/conversation/mysql.py`          | 65              | 5                       |
| PostgreSQL       | `persistence/conversation/postgres.py`       | 89 (+schema:88) | 10                      |
| Async SQLite     | `persistence/conversation/async_sqlite.py`   | 43              | 13                      |
| Async MySQL      | `persistence/conversation/async_mysql.py`    | 65              | 13                      |
| Async PostgreSQL | `persistence/conversation/async_postgres.py` | 63              | 13                      |
| Turso/LibSQL     | `persistence/conversation/turso.py`          | 66              | 9                       |
| SingleStore      | `persistence/conversation/singlestore.py`    | 51              | 7                       |
| Supabase         | `persistence/conversation/supabase.py`       | 68              | 9                       |
| SurrealDB        | `persistence/conversation/surrealdb.py`      | 57              | 8                       |
| **Total**        | **9 backends**                               |                 | **52 injection points** |

Additionally, `praisonai-agents/praisonaiagents/storage/backends.py:179` (`SQLiteBackend`) accepts `table_name` without validation.

### PoC

```python
#!/usr/bin/env python3
"""
Demonstrates: sqlite.py rejects malicious table_prefix, mysql.py accepts it.
Run: python3 poc.py  (no dependencies required)
"""
import re

payload = "x'; DROP TABLE users; --"

# ── SQLite (patched) ────────────────────────────────────────────────
try:
    if not re.match(r'^[a-zA-Z0-9_]*$', payload):
        raise ValueError("blocked")
    print(f"[SQLite] FAIL — accepted: {payload}")
except ValueError:
    print(f"[SQLite] OK — rejected malicious table_prefix")

# ── MySQL (unpatched) ───────────────────────────────────────────────
sessions_table = f"{payload}sessions"
sql = f"CREATE TABLE IF NOT EXISTS {sessions_table} (session_id VARCHAR(255) PRIMARY KEY)"
print(f"[MySQL]  VULN — generated SQL:\n  {sql}")

# ── PostgreSQL (unpatched — both table_prefix AND schema) ──────────
schema = "public; DROP SCHEMA data CASCADE; --"
sessions_table = f"{schema}.praison_sessions"
sql = f"CREATE SCHEMA IF NOT EXISTS {schema}"
print(f"[Postgres] VULN — schema injection:\n  {sql}")
```

Output:

```
[SQLite] OK — rejected malicious table_prefix
[MySQL]  VULN — generated SQL:
  CREATE TABLE IF NOT EXISTS x'; DROP TABLE users; --sessions (session_id VARCHAR(255) PRIMARY KEY)
[Postgres] VULN — schema injection:
  CREATE SCHEMA IF NOT EXISTS public; DROP SCHEMA data CASCADE; --
```

### Vulnerable code (mysql.py, representative)

```python
# mysql.py:65-67 — NO validation
self.table_prefix = table_prefix                    # ← raw input
self.sessions_table = f"{table_prefix}sessions"     # ← into identifier
self.messages_table = f"{table_prefix}messages"

# mysql.py:105 — straight into DDL
cur.execute(f"""
    CREATE TABLE IF NOT EXISTS {self.sessions_table} (
        session_id VARCHAR(255) PRIMARY KEY, ...
    )
""")
```

Compare with the patched `sqlite.py:52`:

```python
# sqlite.py:52-53 — HAS validation
if not re.match(r'^[a-zA-Z0-9_]*$', table_prefix):
    raise ValueError("table_prefix must contain only alphanumeric characters and underscores")
```

### Impact

When `table_prefix` originates from untrusted input — multi-tenant tenant names, API request parameters, user-editable config — an attacker achieves **arbitrary SQL execution** against the backing database. The injected SQL runs in the context of DDL and DML operations (CREATE TABLE, INSERT, SELECT, DELETE), giving the attacker read/write/delete access to the entire database.

PostgreSQL's `schema` parameter adds a second injection vector in DDL (`CREATE SCHEMA IF NOT EXISTS {schema}`).

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-rg3h-x3jw-7jm5
- https://nvd.nist.gov/vuln/detail/CVE-2026-41496
- https://github.com/MervinPraison/PraisonAI
