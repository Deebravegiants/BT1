# [M] Hi.Events: SQL Injection via Unvalidated sort_by Query Parameter in Multiple Repository Classes

## Summary
Severity: Medium
Advisory: CVE-2026-34455
Aliases: GHSA-2qcp-24fh-fx6p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-01
Source: https://osv.dev/vulnerability/CVE-2026-34455
Type: osv

## Details
Hi.Events is an open-source event management and ticket selling platform. From version 0.8.0-beta.1 to before version 1.7.1-beta, multiple repository classes pass the user-supplied sort_by query parameter directly to Eloquent's orderBy() without validation, enabling SQL injection. The application uses PostgreSQL which supports stacked queries. This issue has been patched in version 1.7.1-beta.

## References
- https://github.com/HiEventsDev/Hi.Events/releases/tag/v1.7.1-beta
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34455.json
- https://github.com/HiEventsDev/Hi.Events/security/advisories/GHSA-2qcp-24fh-fx6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-34455
- https://github.com/HiEventsDev/Hi.Events/commit/01e1aee28d7249f235fdcca8e3a34e88214dcde9
- https://github.com/HiEventsDev/Hi.Events/pull/1128
