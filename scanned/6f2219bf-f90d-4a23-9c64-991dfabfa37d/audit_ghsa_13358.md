# [M] Pimcore admin UI vulnerable to Cross-site Scripting in 2 factor authentication setup page

## Summary
Severity: Medium
Advisory: GHSA-hqv9-6jqw-9g8m
CVE: CVE-2023-37280
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-12
Source: https://github.com/advisories/GHSA-hqv9-6jqw-9g8m
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.0.3

## Details
### Summary

Unauthenticated HTML Injection / XSS Possible.
Conditions: 2factor authentication must not set before

 Vulnerable Endpoint: /admin/login/2fa-setup

 Vulnerable Param: error=
How it works, So basically any admin, who has not setup 2 factor authentication before is vulnerable for this attack, without need for any form of privilege, causing the application to execute arbitrary scripts / HTML Contents.

Another potential attack vector, as it's a 2fa page and it has QR Code, attacker can replace this QR Code with something he has, leading to increase threat to the admin.

This attack can be used to execute arbitrary scripts or HTML Injection, causing the target application to execute these resulting in cookie steeling, defacement or Injecting phishing URLs on the target application.

### Patches
Update to version 1.0.3 or apply this patches manually
https://github.com/pimcore/admin-ui-classic-bundle/commit/5fcd19bdc89a3fe4cb8ad8c356590e1e4740c743.patch

### Workarounds
Apply patches manually: https://github.com/pimcore/admin-ui-classic-bundle/commit/5fcd19bdc89a3fe4cb8ad8c356590e1e4740c743.patch

### References
https://huntr.dev/bounties/1fa1cc3b-75ff-4d34-99ae-4a705eb623e7/

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-hqv9-6jqw-9g8m
- https://nvd.nist.gov/vuln/detail/CVE-2023-37280
- https://github.com/pimcore/admin-ui-classic-bundle/pull/147
- https://github.com/pimcore/admin-ui-classic-bundle/commit/5fcd19bdc89a3fe4cb8ad8c356590e1e4740c743
- https://github.com/pimcore/admin-ui-classic-bundle
- https://huntr.dev/bounties/1fa1cc3b-75ff-4d34-99ae-4a705eb623e7
