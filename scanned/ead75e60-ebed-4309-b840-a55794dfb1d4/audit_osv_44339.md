# [H] Cross-tenant database retargeting via dot/NUL injection in namespace strings in the C++ Driver

## Summary
Severity: High
Advisory: CVE-2026-81522
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81522
Type: osv

## Details
A weakness in the MongoDB C++ Driver's handling of caller-supplied namespace identifiers allows special characters embedded in those identifiers. An application that builds a namespace identifier from untrusted input without validating it may therefore have its operation directed at a different target than intended. This can result in limited unauthorized read and write access to data belonging to another logical tenant of the affected application.

## References
- https://github.com/mongodb/mongo-cxx-driver/releases/tag/r4.5.1
- https://jira.mongodb.org/browse/CXX-3552
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81522.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81522
