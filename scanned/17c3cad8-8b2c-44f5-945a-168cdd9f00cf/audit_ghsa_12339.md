# [H] Directory Traversal in JFinalCMS

## Summary
Severity: High
Advisory: GHSA-7x2g-4jvc-4x6p
CVE: CVE-2023-50449
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-10
Source: https://github.com/advisories/GHSA-7x2g-4jvc-4x6p
Type: github-advisory

## Affected
- Maven: `com.jfinal:jfinal` — affected >=0

## Details
JFinalCMS 5.0.0 could allow a remote attacker to read files via ../ Directory Traversal in the /common/down/file fileKey parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50449
- https://gitee.com/heyewei/JFinalcms/issues/I7WGC6
- https://github.com/jfinal/jfinal
