# [M] ViMbAdmin Cross-site Scripting Vulnerabilities

## Summary
Severity: Medium
Advisory: GHSA-jj4j-cwgq-fx7g
CVE: CVE-2017-5870
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jj4j-cwgq-fx7g
Type: github-advisory

## Affected
- Packagist: `opensolutions/vimbadmin` — affected >=0

## Details
Multiple cross-site scripting (XSS) vulnerabilities in ViMbAdmin 3.0.15 allow remote attackers to inject arbitrary web script or HTML via the (1) domain or (2) transport parameter to domain/add; the (3) name parameter to mailbox/add/did/<domain id>; the (4) goto parameter to alias/add/did/<domain id>; or the (5) captchatext parameter to auth/lost-password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-5870
- https://github.com/opensolutions/ViMbAdmin
- https://web.archive.org/web/20201208133828/https://sysdream.com/news/lab/2017-05-03-cve-2017-5870-multiple-xss-vulnerabilities-in-vimbadmin
- http://www.openwall.com/lists/oss-security/2017/05/03/8
