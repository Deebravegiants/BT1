# [M] CVE-2021-41176

## Summary
Severity: Medium
Advisory: CVE-2021-41176
Aliases: GHSA-m49f-hcxp-6hm6
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N)
Published: 2021-10-25
Source: https://osv.dev/vulnerability/CVE-2021-41176
Type: osv

## Details
Pterodactyl is an open-source game server management panel built with PHP 7, React, and Go. In affected versions of Pterodactyl a malicious user can trigger a user logout if a signed in user visits a malicious website that makes a request to the Panel's sign-out endpoint. This requires a targeted attack against a specific Panel instance, and serves only to sign a user out. **No user details are leaked, nor is any user data affected, this is simply an annoyance at worst.** This is fixed in version 1.6.3.

## References
- https://github.com/pterodactyl/panel/releases/tag/v1.6.3
- https://github.com/pterodactyl/panel/security/advisories/GHSA-m49f-hcxp-6hm6
- https://github.com/pterodactyl/panel/commit/45999ba4ee1b2dcb12b4a2fa2cedfb6b5d66fac2
