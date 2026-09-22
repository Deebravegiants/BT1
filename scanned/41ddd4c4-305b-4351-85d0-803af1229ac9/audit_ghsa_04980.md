# [H] LangChain4j: SQL injection via metadata filters in langchain4j-mariadb and langchain4j-pgvector

## Summary
Severity: High
Advisory: GHSA-2mfg-cc43-9pcj
CVE: CVE-2026-55405
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2026-06-17
Source: https://github.com/advisories/GHSA-2mfg-cc43-9pcj
Type: github-advisory

## Affected
- Maven: `dev.langchain4j:langchain4j-mariadb` — affected >=0 <1.2.1-beta8
- Maven: `dev.langchain4j:langchain4j-mariadb` — affected >=1.3.0-beta9 <1.5.1-beta11
- Maven: `dev.langchain4j:langchain4j-mariadb` — affected >=1.6.0-beta12 <1.11.8-beta19
- Maven: `dev.langchain4j:langchain4j-mariadb` — affected >=1.12.1-beta21 <1.16.3-beta26
- Maven: `dev.langchain4j:langchain4j-pgvector` — affected >=0 <1.2.1-beta8
- Maven: `dev.langchain4j:langchain4j-pgvector` — affected >=1.3.0-beta9 <1.5.1-beta11
- Maven: `dev.langchain4j:langchain4j-pgvector` — affected >=1.6.0-beta12 <1.11.8-beta19
- Maven: `dev.langchain4j:langchain4j-pgvector` — affected >=1.12.1-beta21 <1.16.3-beta26

## Details
### Summary
The MariaDB and pgvector embedding stores build metadata-filter SQL by string-concatenating
filter **keys** (and, in MariaDB, string **values**) directly into the query without adequate
escaping. A crafted metadata key in `EmbeddingSearchRequest.filter()` can break out of its SQL
context and inject arbitrary SQL into the statements executed by the stores' search and
`removeAll(Filter)` operations.

### Details
**pgvector — JSON mode (default, `COMBINED_JSON` / `COMBINED_JSONB`).** `JSONFilterMapper`
places the key inside a single-quoted SQL literal (the JSON key of the `->>` operator) with no
escaping:

    (metadata->>'<key>')::text

A key containing a single quote breaks out, e.g.
`metadataKey("')::text IS NOT NULL OR pg_sleep(1) IS NOT NULL --")` injects a live `pg_sleep(1)`
(observable as a delay; exploitable for blind data extraction).

**pgvector — column mode (`COLUMN_PER_KEY`).** `ColumnFilterMapper` used the key as a bare,
unquoted, unvalidated SQL identifier (`<key>::<type>`), so a key such as `1=1 OR true --`
injects directly.

**MariaDB — JSON mode (default).** `JSONFilterMapper` placed the key inside the JSON path literal
`'$.<key>'` unescaped (same break-out mechanism). Additionally, `MariaDbFilterMapper.formatValue()`
escaped `'` but not `\`; because MariaDB treats backslash as an escape character by default, a
string value ending in a backslash could also break out of its literal.

**MariaDB — column mode (`COLUMN_PER_KEY`).** `ColumnFilterMapper` fell back to the raw,
unescaped key when the driver could not quote it as an identifier (e.g. a
character).

The filter key is the runtime injection surface; both stores' `search()` (including pgvector's
HYBRID mode) and `removeAll(Filter)` are affected. Add/upsert operations a
parameterized and not affected.

### Impact
Applications that allow attacker-influenced metadata filter keys (e.g. use
LLM-generated filters) to reach these stores are exposed to SQL injection: blind data
exfiltration, denial of service via sleep functions, and — through `remove
deletion of arbitrary rows. Applications using only hard-coded, developer-defined filter keys
are not reachable.

### Patches
Fixed in `langchain4j-mariadb` and `langchain4j-pgvector` 1.16.3-beta26:
- JSON filter keys are escaped before being embedded in the SQL string lit
  quotes doubled, correct for PostgreSQL `standard_conforming_strings = on`; MariaDB: backslash
  and single quote).
- MariaDB string values escape both `\` and `'`.
- Column-mode keys are validated/quoted as identifiers and rejected when u
  concatenated as raw SQL.

### Workarounds
- Do not pass untrusted input as metadata filter keys.
- Restrict filter keys to a known allow-list at the application layer.

### References
- pgvector: `JSONFilterMapper`, `ColumnFilterMapper`
- MariaDB: `JSONFilterMapper`, `MariaDbFilterMapper`, `ColumnFilterMapper`

## References
- https://github.com/langchain4j/langchain4j/security/advisories/GHSA-2mfg-cc43-9pcj
- https://github.com/langchain4j/langchain4j
