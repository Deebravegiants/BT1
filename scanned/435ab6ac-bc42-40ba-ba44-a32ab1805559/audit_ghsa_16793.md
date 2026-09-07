# [H] eZ Platform Admin UI Password reset vulnerability

## Summary
Severity: High
Advisory: GHSA-hfpp-2vhw-qq43
CWE: CWE-307
Ecosystem: Packagist
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-hfpp-2vhw-qq43
Type: github-advisory

## Affected
- Packagist: `ezsystems/ezplatform-user` — affected >=1.0.0 <1.0.1

## Details
his Security Update fixes a severe vulnerability in the eZ Platform Admin UI, and we recommend that you install it as soon as possible. It affects eZ Platform 2.x.
 
The functionality for resetting a forgotten password is vulnerable to brute force attack. Depending on configuration and other circumstances an attacker may exploit this to gain control over user accounts. The update ensures such an attack is exceedingly unlikely to succeed.
 
You may want to consider a configuration change to further strengthen your security. By default a password reset request is valid for 1 hour. Reducing this time will make attacks even more difficult, but ensure there is enough time left to account for email delivery delays, and user delays. See documentation at https://doc.ezplatform.com/en/latest/guide/user_management/#changing-and-recovering-passwords

To install, use Composer to update to one of the "Resolving versions" mentioned above. If you use eZ Platform 2.5, update ezsystems/ezplatform-user to v1.0.1. If you use eZ Platform 2.4, update ezsystems/ezplatform-admin-ui to v1.4.6, and ezsystems/ezplatform-admin-ui-modules to v1.4.4, and ezsystems/repository-forms to v2.4.5)

## References
- https://github.com/FriendsOfPHP/security-advisories/blob/master/ezsystems/ezplatform-user/2019-04-03-1.yaml
- https://github.com/ezsystems/ezplatform-user
- https://web.archive.org/web/20201025103933/https://share.ez.no/community-project/security-advisories/ezsa-2019-002-password-reset-vulnerability
