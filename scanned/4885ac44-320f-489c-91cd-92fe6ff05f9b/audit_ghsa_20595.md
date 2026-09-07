# [H] Sandbox Escape by math function in smarty

## Summary
Severity: High
Advisory: GHSA-29gp-2c3m-3j6m
CVE: CVE-2021-29454
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-29gp-2c3m-3j6m
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.1.42
- Packagist: `smarty/smarty` — affected >=4.0.0 <4.0.2

## Details
### Impact
Template authors could run arbitrary PHP code by crafting a malicious math string.
If a math string is passed through as user provided data to the math function, external users could run arbitrary PHP code by crafting a malicious math string.

### Patches
Please upgrade to 4.0.2 or 3.1.42 or higher.

### References
See [documentation on Math function](https://www.smarty.net/docs/en/language.function.math.tpl).

### For more information
If you have any questions or comments about this advisory please open an issue in [the Smarty repo](https://github.com/smarty-php/smarty)

## References
- https://github.com/smarty-php/smarty/security/advisories/GHSA-29gp-2c3m-3j6m
- https://nvd.nist.gov/vuln/detail/CVE-2021-29454
- https://github.com/smarty-php/smarty/commit/215d81a9fa3cd63d82fb3ab56ecaf97cf1e7db71
- https://github.com/FriendsOfPHP/security-advisories/blob/master/smarty/smarty/CVE-2021-29454.yaml
- https://github.com/smarty-php/smarty
- https://github.com/smarty-php/smarty/releases/tag/v3.1.42
- https://github.com/smarty-php/smarty/releases/tag/v4.0.2
- https://lists.debian.org/debian-lts-announce/2022/05/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BRAJVDRGCIY5UZ2PQHKDTT7RMKG6WJQQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L777JIBIWJV34HS7LXPIDWASG7TT4LNI
- https://packagist.org/packages/smarty/smarty
- https://security.gentoo.org/glsa/202209-09
- https://www.debian.org/security/2022/dsa-5151
- https://www.smarty.net/docs/en/language.function.math.tpl
