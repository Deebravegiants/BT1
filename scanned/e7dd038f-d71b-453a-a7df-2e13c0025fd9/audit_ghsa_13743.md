# [M] Symfony possible session fixation vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m2wj-r6g3-fxfx
CVE: CVE-2023-46733
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-11-12
Source: https://github.com/advisories/GHSA-m2wj-r6g3-fxfx
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=5.4.21 <5.4.31
- Packagist: `symfony/security-http` — affected >=6.2.7 <6.3.8
- Packagist: `symfony/symfony` — affected >=5.4.21 <5.4.31
- Packagist: `symfony/symfony` — affected >=6.2.7 <6.3.8

## Details
### Description

SessionStrategyListener does not always migrate the session after a successful login. It only migrate the session when the logged-in user identifier changes. In some use cases, the user identifier doesn't change between the verification phase and the successful login, while the token itself changes from one type (partially-authenticated) to another (fully-authenticated). When this happens, the session id should be regenerated to prevent possible session fixations.

### Resolution

Symfony now checks the type of the token in addition to the user identifier before deciding whether the session id should be regenerated.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/dc356499d5ceb86f7cf2b4c7f032eca97061ed74) for branch 5.4.

### Credits

We would like to thank Robert Meijers for reporting the issue and providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-m2wj-r6g3-fxfx
- https://nvd.nist.gov/vuln/detail/CVE-2023-46733
- https://github.com/symfony/symfony/commit/7467bd7e3f888b333102bc664b5e02ef1e7f88b9
- https://github.com/symfony/symfony/commit/dc356499d5ceb86f7cf2b4c7f032eca97061ed74
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2023-46733.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2023-46733
