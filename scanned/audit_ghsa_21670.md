# [H] Code injection in Twig

## Summary
Severity: High
Advisory: GHSA-5mv2-rx3q-4w2v
CVE: CVE-2022-23614
CWE: CWE-74, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-5mv2-rx3q-4w2v
Type: github-advisory

## Affected
- Packagist: `twig/twig` — affected >=2.0.0 <2.14.11
- Packagist: `twig/twig` — affected >=3.0.0 <3.3.8

## Details
# Description

When in a sandbox mode, the `arrow` parameter of the `sort` filter must be a closure to avoid attackers being able to run arbitrary PHP functions.

# Resolution

We now disallow calling non Closure in the `sort` filter like we already did for some other filters.

# Credits

We would like to thank Marlon Starkloff for reporting the issue and Fabien Potencier for fixing the issue.

## References
- https://github.com/twigphp/Twig/security/advisories/GHSA-5mv2-rx3q-4w2v
- https://nvd.nist.gov/vuln/detail/CVE-2022-23614
- https://github.com/twigphp/Twig/commit/22b9dc3c03ee66d7e21d9ed2ca76052b134cb9e9
- https://github.com/twigphp/Twig/commit/2eb33080558611201b55079d07ac88f207b466d5
- https://github.com/FriendsOfPHP/security-advisories/blob/master/twig/twig/CVE-2022-23614.yaml
- https://github.com/twigphp/Twig
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/I2PVV5DUTRUECTIHMTWRI5Z7DVNYQ2YO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OTN4273U4RHVIXED64T7DSMJ3VYTPRE7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/PECHIY2XLWUH2WLCNPDGNFMPHPRPCEDZ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SIGZCFSYLPP7UVJ4E4NLHSOQSKYNXSAD
- https://symfony.com/blog/twig-security-release-disallow-non-closures-in-the-sort-filter
- https://www.debian.org/security/2022/dsa-5107
