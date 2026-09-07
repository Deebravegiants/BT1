# [H] PrestaShop module ps_facetedsearch might be vulnerable from CVE-2017-9841

## Summary
Severity: High
Advisory: GHSA-f884-gm86-cg3q
Ecosystem: Packagist
Published: 2020-01-07
Source: https://github.com/advisories/GHSA-f884-gm86-cg3q
Type: github-advisory

## Affected
- Packagist: `prestashop/ps_facetedsearch` — affected >=0 <3.4.1

## Details
### Impact

We have identified that some ps_facetedsearch module ZIP archives have been built with phpunit dev dependencies. PHPUnit contains a php script that would allow, on a webserver, an attacker to perform a RCE.

This vulnerability impacts
- phpunit before 4.8.28 and 5.x before 5.6.3 as reported in [CVE-2017-9841](https://nvd.nist.gov/vuln/detail/CVE-2017-9841)
- phpunit >= 5.63 before 7.5.19 and 8.5.1 (this is a newly found vulnerability that is currently being submitted as a CVE after disclosure was provided to phpunit maintainers)

### Patches

In the [security patch](https://github.com/PrestaShop/ps_facetedsearch/releases/tag/v3.4.1), we look for the unwanted vendor/phpunit folder and remove it if we find it. This allows users to fix the security issue when upgrading.

### Workarounds
Users can also simply remove the unwanted vendor/phpunit folder.

### References
https://nvd.nist.gov/vuln/detail/CVE-2017-9841

### For more information
If you have any questions or comments about this advisory, email us at security@prestashop.com

## References
- https://github.com/PrestaShop/ps_facetedsearch/security/advisories/GHSA-f884-gm86-cg3q
- https://github.com/PrestaShop/ps_facetedsearch/commit/47c4785a21ee3b1734b2d46f044f9659a151feca
