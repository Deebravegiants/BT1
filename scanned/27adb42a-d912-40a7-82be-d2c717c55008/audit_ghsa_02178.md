# [M] Exposed phpinfo() leadked via documentation files

## Summary
Severity: Medium
Advisory: GHSA-cvh5-p6r6-g2qc
CVE: CVE-2021-37704
CWE: CWE-200, CWE-668
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2021-08-30
Source: https://github.com/advisories/GHSA-cvh5-p6r6-g2qc
Type: github-advisory

## Affected
- Packagist: `phpfastcache/phpfastcache` — affected >=0 <6.1.5
- Packagist: `phpfastcache/phpfastcache` — affected >=7.0.0 <7.1.2
- Packagist: `phpfastcache/phpfastcache` — affected >=8.0.0 <8.0.7

## Details
### Impact
The `phpinfo()` can be exposed if the `/vendor` is not protected from public access. This is a rare situation today since the vendor directory is often located outside the web directory or protected via server rule (.htaccess, etc).

### Patches
Only the v6, v7 and v8 will be patched respectively in 8.0.7, 7.1.2, 6.1.5.
Older versions such as v5, v4 are not longer supported and will **NOT** be patched.

### Workarounds
Protect the `/vendor` directory from public access.

### References
The first issue revealing this vulnerability is located here: https://github.com/flextype/flextype/issues/567
V6 fix: https://github.com/PHPSocialNetwork/phpfastcache/pull/815
V7 fix: https://github.com/PHPSocialNetwork/phpfastcache/pull/814
V8 fix: https://github.com/PHPSocialNetwork/phpfastcache/pull/813

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [our issue tracker](https://github.com/PHPSocialNetwork/phpfastcache/issues)
* Email us at [security@geolim4.com](mailto:security@geolim4.com)

## References
- https://github.com/PHPSocialNetwork/phpfastcache/security/advisories/GHSA-cvh5-p6r6-g2qc
- https://nvd.nist.gov/vuln/detail/CVE-2021-37704
- https://github.com/flextype/flextype/issues/567
- https://github.com/PHPSocialNetwork/phpfastcache/pull/813
- https://github.com/PHPSocialNetwork/phpfastcache/pull/814
- https://github.com/PHPSocialNetwork/phpfastcache/pull/815
- https://github.com/PHPSocialNetwork/phpfastcache/commit/41a77d0d8f126dbd6fbedcd9e6a82e86cdaafa51
- https://github.com/PHPSocialNetwork/phpfastcache/blob/master/CHANGELOG.md#807
- https://packagist.org/packages/phpfastcache/phpfastcache
