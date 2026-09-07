# [M] Reflected cross site scripting

## Summary
Severity: Medium
Advisory: GHSA-vcpr-hm2m-gjjj
CVE: CVE-2023-28475
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-04-28
Source: https://github.com/advisories/GHSA-vcpr-hm2m-gjjj
Type: github-advisory

## Affected
- Packagist: `concrete5/concrete5` — affected >=0 <9.2.0

## Details
Concrete CMS (previously concrete5) before 9.2 is vulnerable to Reflected XSS on the Reply form because msgID was not sanitized.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28475
- https://github.com/concretecms/concretecms/commit/861ba66d248165c9ee9d6d11a0457908b97d68f0
- https://concretecms.com
- https://www.concretecms.org/about/project-news/security/2023-11-09-security-blog-about-updated-cves-and-new-release
- https://www.concretecms.org/about/project-news/security/concrete-cms-security-advisory-2023-04-20
