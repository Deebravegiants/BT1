# [H] agno contains a SQL injection vulnerability

## Summary
Severity: High
Advisory: GHSA-82m5-3pcp-hccq
CVE: CVE-2026-10105
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-82m5-3pcp-hccq
Type: github-advisory

## Affected
- PyPI: `agno` — affected >=0

## Details
agno 2.6.5 contains a SQL injection vulnerability in the ClickHouse vector database backend that allows attackers to inject arbitrary SQL expressions by supplying malicious metadata keys and values to the delete_by_metadata() method. Attackers can exploit the unsafe f-string interpolation in clickhousedb.py to delete all rows, target specific rows, or extract information through error-based or blind SQL injection techniques.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-10105
- https://github.com/agno-agi/agno/issues/7866
- https://github.com/agno-agi/agno/pull/7883
- https://github.com/agno-agi/agno/pull/7883/changes/26a7439b803c0ccc9a58ee53572d8088a678923f
- https://github.com/agno-agi/agno/pull/7883/changes/a0ec99305e782e68ba26f5966c53ad50b5f40132
- https://github.com/agno-agi/agno
- https://www.vulncheck.com/advisories/agno-sql-injection-via-clickhouse-delete-by-metadata
