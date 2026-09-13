# [C] PHP Code Injection by malicious function name in smarty

## Summary
Severity: Critical
Advisory: GHSA-3rpf-5rqv-689q
CVE: CVE-2021-26120
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-02-26
Source: https://github.com/advisories/GHSA-3rpf-5rqv-689q
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.1.39

## Details
Template authors could inject php code by choosing a malicous {function} name. Sites that cannot fully trust template authors should update as soon as possible. Please upgrade to 3.1.39 or higher.

## References
- https://github.com/smarty-php/smarty/security/advisories/GHSA-3rpf-5rqv-689q
- https://nvd.nist.gov/vuln/detail/CVE-2021-26120
- https://github.com/smarty-php/smarty/commit/165f1bd4d2eec328cfeaca517a725b46001de838
- https://github.com/FriendsOfPHP/security-advisories/blob/master/smarty/smarty/CVE-2021-26120.yaml
- https://github.com/smarty-php/smarty
- https://github.com/smarty-php/smarty/blob/master/CHANGELOG.md
- https://github.com/smarty-php/smarty/blob/master/CHANGELOG.md#3139---2021-02-17
- https://lists.debian.org/debian-lts-announce/2021/04/msg00004.html
- https://lists.debian.org/debian-lts-announce/2021/04/msg00014.html
- https://security.gentoo.org/glsa/202105-06
- https://srcincite.io/blog/2021/02/18/smarty-template-engine-multiple-sandbox-escape-vulnerabilities.html
- https://www.debian.org/security/2022/dsa-5151
