# [H] Saloon has insecure deserialization in AccessTokenAuthenticator

## Summary
Severity: High
Advisory: GHSA-rf88-776r-rcq9
CVE: CVE-2026-33942
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-rf88-776r-rcq9
Type: github-advisory

## Affected
- Packagist: `saloonphp/saloon` — affected >=0 <4.0.0

## Details
### Impact
Users of the OAuth2 utilities in Saloon, specifically the `AccessTokenAuthenticator` class.

### Patches
Upgrade to Saloon v4+

Upgrade guide: https://docs.saloon.dev/upgrade/upgrading-from-v3-to-v4

### Description
The Saloon PHP library used PHP's unserialize() in AccessTokenAuthenticator::unserialize() to restore OAuth token state from cache or storage, with allowed_classes => true. An attacker who can control the serialized string (e.g. by overwriting a cached token file or via another injection) can supply a serialized "gadget" object. When unserialize() runs, PHP instantiates that object and runs its magic methods (__wakeup, __destruct, etc.), leading to object injection. In environments with common dependencies (e.g. Monolog), this can be chained to remote code execution (RCE). The fix removes PHP serialization from the AccessTokenAuthenticator class requiring users to store and resolve the authenticator manually.

### Credits
Saloon thanks @HuajiHD for finding the issue and recommending solutions and @jonpurvis for applying the fix.

## References
- https://github.com/saloonphp/saloon/security/advisories/GHSA-rf88-776r-rcq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33942
- https://docs.saloon.dev/upgrade/upgrading-from-v3-to-v4
- https://github.com/saloonphp/saloon
