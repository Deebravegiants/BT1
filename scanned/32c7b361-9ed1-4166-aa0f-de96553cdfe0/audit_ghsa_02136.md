# [C] Steam Socialite Provider v1 does not correctly validate openid server

## Summary
Severity: Critical
Advisory: GHSA-hhw9-35p2-q2c5
CWE: CWE-346
Ecosystem: Packagist
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-hhw9-35p2-q2c5
Type: github-advisory

## Affected
- Packagist: `socialiteproviders/steam` — affected >=0 <3.0

## Details
### Impact
The outdated version 1 of the Steam Socialite Provider doesn't check properly if the login comes from `steamcommunity.com`, allowing a malicious actor to substitute their own openID server.

### Patches
This vulnerability only affects the outdated v1.x versions of the package. These are no longer maintained, users should upgrade to v3 or v4, which use a hardcoded endpoint to verify the login.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [SocialiteProviders/Providers](https://github.com/SocialiteProviders/Providers)
* Email us at [socialite@atymic.dev](mailto:socialite@atymic.dev)

## References
- https://github.com/SocialiteProviders/Steam/security/advisories/GHSA-hhw9-35p2-q2c5
- https://packagist.org/packages/socialiteproviders/steam
