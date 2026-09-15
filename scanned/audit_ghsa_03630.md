# [M] Object injection in cookie driver in phpfastcache

## Summary
Severity: Medium
Advisory: GHSA-484f-743f-6jx2
CVE: CVE-2019-16774
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-12-12
Source: https://github.com/advisories/GHSA-484f-743f-6jx2
Type: github-advisory

## Affected
- Packagist: `phpfastcache/phpfastcache` — affected >=5.0.0 <5.0.13

## Details
### Impact
An possible object injection has been discovered in cookie driver prior 5.0.13 versions (of 5.x releases).

### Patches
The issue has been addressed by enforcing JSON conversion when deserializing

### Workarounds
If you can't fix it, use another driver such as "Files" (Filesystem)

### References
Fixing release: https://github.com/PHPSocialNetwork/phpfastcache/releases/tag/5.0.13

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the issue tracker](https://github.com/PHPSocialNetwork/phpfastcache/issues)
* Email us at [security@geolim4.com](mailto:security@geolim4.com)

## References
- https://github.com/PHPSocialNetwork/phpfastcache/security/advisories/GHSA-484f-743f-6jx2
- https://nvd.nist.gov/vuln/detail/CVE-2019-16774
- https://github.com/PHPSocialNetwork/phpfastcache/commit/c4527205cb7a402b595790c74310791f5b04a1a4
- https://github.com/PHPSocialNetwork/phpfastcache
- https://github.com/PHPSocialNetwork/phpfastcache/releases/tag/5.0.13
- https://github.com/advisories/GHSA-484f-743f-6jx2
