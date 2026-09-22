# [H] Apache Neethi: Missing global alternative-output budget across policy computation paths

## Summary
Severity: High
Advisory: CVE-2026-66143
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-24
Source: https://osv.dev/vulnerability/CVE-2026-66143
Type: osv

## Details
It is possible to bypass the maximum number of normalized policy alternatives that was introduced in Apache Neethi 3.2.2 via certain crafted policies, which may lead to a denial of service attack via resource consumption. Users are recommended to upgrade to version 3.2.3, which fixes this issue.

## References
- http://www.openwall.com/lists/oss-security/2026/07/24/9
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66143.json
- https://lists.apache.org/thread/s6o6p5pvcbcsk54dlg6j699t5gxol28w
- https://nvd.nist.gov/vuln/detail/CVE-2026-66143
