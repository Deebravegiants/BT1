# [C] Apache Allura: Git command injection

## Summary
Severity: Critical
Advisory: CVE-2026-73240
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-73240
Type: osv

## Details
Specifically crafted inputs may lead to git argument injection in Apache Allura.

This issue affects Apache Allura: before 1.19.1.

Users are recommended to upgrade to version 1.19.1, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/08/12/19
- https://allura.apache.org/posts/2026-allura-1.19.1.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73240.json
- https://lists.apache.org/thread/10gnxblhomk2z4gxcyyb4t3p4zxsdddv
- https://nvd.nist.gov/vuln/detail/CVE-2026-73240
