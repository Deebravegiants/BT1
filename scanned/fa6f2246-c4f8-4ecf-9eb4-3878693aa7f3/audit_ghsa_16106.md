# [H] Symfony has an Authentication Bypass via RememberMe

## Summary
Severity: High
Advisory: GHSA-cg23-qf8f-62rr
CVE: CVE-2024-51996
CWE: CWE-287, CWE-289
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-13
Source: https://github.com/advisories/GHSA-cg23-qf8f-62rr
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=5.3.0 <5.4.47
- Packagist: `symfony/security-http` — affected >=6.0.0-BETA1 <6.4.15
- Packagist: `symfony/security-http` — affected >=7.0.0-BETA1 <7.1.8

## Details
### Description

When consuming a persisted remember-me cookie, Symfony does not check if the username persisted in the database matches the username attached with the cookie, leading to authentication bypass.

### Resolution

The `PersistentRememberMeHandler` class now ensures the submitted username is the cookie owner.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/81354d392c5f0b7a52bcbd729d6f82501e94135a) for branch 5.4.

### Credits

We would like to thank Moritz Rauch - Pentryx AG for reporting the issue and Jérémy Derussé for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-cg23-qf8f-62rr
- https://nvd.nist.gov/vuln/detail/CVE-2024-51996
- https://github.com/symfony/symfony/commit/81354d392c5f0b7a52bcbd729d6f82501e94135a
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2024-51996.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2024-51996.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2024-51996
