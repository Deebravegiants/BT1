# [C] CVE-2021-33204

## Summary
Severity: Critical
Advisory: CVE-2021-33204
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-19
Source: https://osv.dev/vulnerability/CVE-2021-33204
Type: osv

## Details
In the pg_partman (aka PG Partition Manager) extension before 4.5.1 for PostgreSQL, arbitrary code execution can be achieved via SECURITY DEFINER functions because an explicit search_path is not set.

## References
- https://security.netapp.com/advisory/ntap-20210625-0006/
- https://github.com/pgpartman/pg_partman/commit/0b6565ad378c358f8a6cd1d48ddc482eb7f854d3
- https://github.com/pgpartman/pg_partman/compare/v4.5.0...v4.5.1
