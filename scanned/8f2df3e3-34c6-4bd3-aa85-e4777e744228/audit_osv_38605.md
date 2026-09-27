# [C] Electric: SQL Injection via ORDER BY Parameter in Shape API

## Summary
Severity: Critical
Advisory: CVE-2026-40906
Aliases: GHSA-h5rg-pxx7-r2hj
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40906
Type: osv

## Details
Electric is a Postgres sync engine. From 1.1.12 to before 1.5.0, the order_by parameter in the ElectricSQL /v1/shape API is vulnerable to error-based SQL injection, allowing any authenticated user to read, write, and destroy the full contents of the underlying PostgreSQL database through crafted ORDER BY expressions. This vulnerability is fixed in 1.5.0.

## References
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40906.json
- https://access.redhat.com/security/cve/CVE-2026-40906
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40906.json
- https://github.com/electric-sql/electric/security/advisories/GHSA-h5rg-pxx7-r2hj
- https://nvd.nist.gov/vuln/detail/CVE-2026-40906
- https://bugzilla.redhat.com/show_bug.cgi?id=2460291
- https://github.com/electric-sql/electric/pull/4081
