# [H] TimescaleDB uses untrusted search path during extension upgrade

## Summary
Severity: High
Advisory: CVE-2026-29089
Aliases: GHSA-vgp2-jj5c-828m
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/CVE-2026-29089
Type: osv

## Details
TimescaleDB is a time-series database for high-performance real-time analytics packaged as a Postgres extension. From version 2.23.0 to 2.25.1, PostgreSQL uses the search_path setting to locate unqualified database objects (tables, functions, operators). If the search_path includes user-writable schemas a malicious user can create functions in that schema that shadow builtin postgres functions and will be called instead of the postgres functions leading to arbitrary code execution during extension upgrade. This issue has been patched in version 2.25.2.

## References
- https://github.com/timescale/timescaledb/releases/tag/2.25.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/29xxx/CVE-2026-29089.json
- https://github.com/timescale/timescaledb/security/advisories/GHSA-vgp2-jj5c-828m
- https://nvd.nist.gov/vuln/detail/CVE-2026-29089
- https://github.com/timescale/timescaledb/commit/9a8f7f8bdeb99e6abae0786ffe526791a8628ce3
- https://github.com/timescale/timescaledb/pull/9331
