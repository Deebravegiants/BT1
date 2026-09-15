# [H] Sandbox escape through template_object in smarty

## Summary
Severity: High
Advisory: GHSA-w5hr-jm4j-9jvq
CVE: CVE-2021-26119
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-03-02
Source: https://github.com/advisories/GHSA-w5hr-jm4j-9jvq
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.1.39

## Details
Sandbox protection could be bypassed through access to an internal Smarty object that should have been blocked. Sites that rely on [Smarty Security features](https://www.smarty.net/docs/en/advanced.features.tpl) should upgrade as soon as possible. Please upgrade to 3.1.39 or higher.

## References
- https://github.com/smarty-php/smarty/security/advisories/GHSA-w5hr-jm4j-9jvq
- https://nvd.nist.gov/vuln/detail/CVE-2021-26119
- https://github.com/FriendsOfPHP/security-advisories/blob/master/smarty/smarty/CVE-2021-26119.yaml
- https://github.com/smarty-php/smarty
- https://github.com/smarty-php/smarty/blob/master/CHANGELOG.md
- https://lists.debian.org/debian-lts-announce/2021/04/msg00004.html
- https://lists.debian.org/debian-lts-announce/2021/04/msg00014.html
- https://security.gentoo.org/glsa/202105-06
- https://srcincite.io/blog/2021/02/18/smarty-template-engine-multiple-sandbox-escape-vulnerabilities.html
- https://www.debian.org/security/2022/dsa-5151
