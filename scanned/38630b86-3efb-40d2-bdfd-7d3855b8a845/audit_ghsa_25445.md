# [H] Twig remote code execution in templates

## Summary
Severity: High
Advisory: GHSA-xw83-pwrm-9j74
CVE: CVE-2015-7809
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-xw83-pwrm-9j74
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=0 <1.20.0

## Details
The `displayBlock` function `Template.php` in Sensio Labs Twig before 1.20.0, when Sandbox mode is enabled, allows remote attackers to execute arbitrary code via the `_self` variable in a template.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-7809
- https://github.com/twigphp/Twig/pull/1759
- https://github.com/twigphp/Twig/commit/30be07759a3de2558da5224f127d052ecf492e8f
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2015-7809.yaml
- https://github.com/twigphp/Twig
- https://symfony.com/blog/security-release-twig-1-20-0
- http://openwall.com/lists/oss-security/2015/08/21/3
- http://openwall.com/lists/oss-security/2015/10/11/2
- http://symfony.com/blog/security-release-twig-1-20-0
- http://www.debian.org/security/2015/dsa-3343
