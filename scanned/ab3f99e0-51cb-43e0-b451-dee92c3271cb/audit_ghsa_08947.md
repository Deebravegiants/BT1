# [H] SQL injection vulnerability in pgAdmin 4 Maintenance Tool

## Summary
Severity: High
Advisory: GHSA-hp84-p2gq-6fvr
CVE: CVE-2026-7815
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-hp84-p2gq-6fvr
Type: github-advisory

## Affected
- PyPI: `pgadmin4` — affected >=0 <9.15

## Details
SQL injection vulnerability in pgAdmin 4 Maintenance Tool.

Four user-supplied JSON fields (buffer_usage_limit, vacuum_parallel, vacuum_index_cleanup, reindex_tablespace) were concatenated directly into the rendered VACUUM/ANALYZE/REINDEX command and passed to psql --command. An authenticated user with the tools_maintenance permission could break out of the option syntax and execute arbitrary SQL on the connected PostgreSQL server. The injected SQL could in turn invoke COPY ... TO PROGRAM to escalate to operating-system command execution on the database host.

Fix introduces server-side allow-listing of all four fields and switches reindex_tablespace from manual quoting to the qtIdent filter.

This issue affects pgAdmin 4: before 9.15.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7815
- https://github.com/pgadmin-org/pgadmin4/issues/9898
- https://github.com/pgadmin-org/pgadmin4/commit/cf53953d9
- https://github.com/pgadmin-org/pgadmin4
