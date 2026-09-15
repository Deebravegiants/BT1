# [M] CVE-2024-57186

## Summary
Severity: Medium
Advisory: CVE-2024-57186
Aliases: GHSA-rq9r-qvwg-829q
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2025-06-10
Source: https://osv.dev/vulnerability/CVE-2024-57186
Type: osv

## Details
In Erxes <1.6.2, an unauthenticated attacker can read arbitrary files from the system using a Path Traversal vulnerability in the /read-file endpoint handler.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57186.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57186
- https://github.com/erxes/erxes/commit/d626070a0fcd435ae29e689aca051ccfb440c2f3
- https://www.sonarsource.com/blog/micro-services-major-headaches-detecting-vulnerabilities-in-erxes-microservices/
