# [M] CVE-2024-23770

## Summary
Severity: Medium
Advisory: CVE-2024-23770
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-01-22
Source: https://osv.dev/vulnerability/CVE-2024-23770
Type: osv

## Details
darkhttpd through 1.15 allows local users to discover credentials (for --auth) by listing processes and their arguments.

## References
- https://github.com/emikulic/darkhttpd/compare/v1.14...v1.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23770.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-23770
- https://github.com/emikulic/darkhttpd/commit/2b339828b2a42a5fda105ea84934957a7d23e35d
- http://www.openwall.com/lists/oss-security/2024/01/25/1
