# [H] PrestaShop gamification module ZIP archives were vulnerable from CVE-2017-9841

## Summary
Severity: High
Advisory: GHSA-769f-539v-f5jg
Ecosystem: Packagist
Published: 2020-01-08
Source: https://github.com/advisories/GHSA-769f-539v-f5jg
Type: github-advisory

## Affected
- Packagist: `prestashop/gamification` — affected >=0 <2.3.2

## Details
### Impact

We have identified that some gamification module ZIP archives have been built with phpunit dev dependencies. PHPUnit contains a php script that would allow, on a webserver, an attacker to perform a RCE.

This vulnerability impacts
- phpunit before 4.8.28 and 5.x before 5.6.3 as reported in [CVE-2017-9841](https://nvd.nist.gov/vuln/detail/CVE-2017-9841)
- phpunit >= 5.63 before 7.5.19 and 8.5.1 (this is a newly found vulnerability that is currently being submitted as a CVE after disclosure was provided to phpunit maintainers)

You can read PrestaShop official statement about this vulnerability [here](https://build.prestashop.com/news/critical-security-vulnerability-in-prestashop-modules/).

### Patches

In the [security patch](https://github.com/PrestaShop/gamification/releases/tag/v2.3.2), we look for the unwanted vendor/phpunit folder and remove it if we find it. This allows users to fix the security issue when upgrading.

### Workarounds
Users can also simply remove the unwanted vendor/phpunit folder.

### References
https://nvd.nist.gov/vuln/detail/CVE-2017-9841

### For more information
If you have any questions or comments about this advisory, email us at security@prestashop.com

## References
- https://github.com/PrestaShop/gamification/security/advisories/GHSA-769f-539v-f5jg
- https://github.com/PrestaShop/gamification/commit/5044bda903a7ea9596c21faa2b9a42244763568c
- https://build.prestashop.com/news/critical-security-vulnerability-in-prestashop-modules
