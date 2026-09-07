# [M] CKEditor 4.0 vulnerability in the HTML Data Processor

## Summary
Severity: Medium
Advisory: GHSA-vcjf-mgcg-jxjq
CVE: CVE-2020-9281
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-07
Source: https://github.com/advisories/GHSA-vcjf-mgcg-jxjq
Type: github-advisory

## Affected
- npm: `ckeditor4` — affected >=0 <4.14.0

## Details
A cross-site scripting (XSS) vulnerability in the HTML Data Processor for CKEditor 4.0 before 4.14.0 allows remote attackers to inject arbitrary web script through a crafted "protected" comment (with the cke_protected syntax).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-9281
- https://github.com/ckeditor/ckeditor4
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7OJ4BSS3VEAEXPNSOOUAXX6RDNECGZNO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L322YA73LCV3TO7ORY45WQDAFJVNKXBE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/M4HHYQ6N452XTCIROFMJOTYEUWSB6FR4
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpujan2021.html
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
