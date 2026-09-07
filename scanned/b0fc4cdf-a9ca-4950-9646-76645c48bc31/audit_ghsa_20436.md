# [H] Access to restricted PHP code by dynamic static class access in smarty

## Summary
Severity: High
Advisory: GHSA-4h9c-v5vg-5m6m
CVE: CVE-2021-21408
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-12
Source: https://github.com/advisories/GHSA-4h9c-v5vg-5m6m
Type: github-advisory

## Affected
- Packagist: `smarty/smarty` — affected >=0 <3.1.43
- Packagist: `smarty/smarty` — affected >=4.0.0 <4.0.3

## Details
### Impact
Template authors could run restricted static php methods.

### Patches
Please upgrade to 3.1.40 or higher.

### References
See the [documentation on Smarty security features](https://www.smarty.net/docs/en/advanced.features.tpl#advanced.features.security) on the static_classes access filter.

### For more information
If you have any questions or comments about this advisory please open an issue in [the Smarty repo](https://github.com/smarty-php/smarty)

## References
- https://github.com/smarty-php/smarty/security/advisories/GHSA-4h9c-v5vg-5m6m
- https://nvd.nist.gov/vuln/detail/CVE-2021-21408
- https://github.com/smarty-php/smarty/commit/19ae410bf56007a5ef24441cdc6414619cfaf664
- https://github.com/FriendsOfPHP/security-advisories/blob/master/smarty/smarty/CVE-2021-21408.yaml
- https://github.com/smarty-php/smarty
- https://github.com/smarty-php/smarty/releases/tag/v3.1.43
- https://github.com/smarty-php/smarty/releases/tag/v4.0.3
- https://lists.debian.org/debian-lts-announce/2022/05/msg00005.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/BRAJVDRGCIY5UZ2PQHKDTT7RMKG6WJQQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L777JIBIWJV34HS7LXPIDWASG7TT4LNI
- https://security.gentoo.org/glsa/202209-09
- https://www.debian.org/security/2022/dsa-5151
