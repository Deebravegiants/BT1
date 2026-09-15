# [H] Pterodactyl vulnerable to 2FA Sniffing

## Summary
Severity: High
Advisory: GHSA-fg52-xjfc-9rh8
CVE: CVE-2019-1020002
CWE: CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-fg52-xjfc-9rh8
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <0.7.14

## Details
**Pterodactyl version 0.7.13 and lower - 2FA Sniffing**

Users who have enabled 2FA protections on their account can unintentionally have their account's existence sniffed by malicious users who enter random credentials into the login fields.

### Impact
Users who have enabled 2FA protections on their account can unintentionally have their account's existence sniffed by malicious users who enter random credentials into the login fields.

A logical mistake was made when the original code was written that would wait to verify the user's password until they had provided 2FA credentials if it was enabled on their account. However, because of this you could enter a bad password for a known email and determine if the account exists if you got redirected to a 2FA page.

### For more information
If you have any questions or comments about this advisory please react out on Discord or email dane@[project name].io.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-vcm9-hx3q-qwj8
- https://nvd.nist.gov/vuln/detail/CVE-2019-1020002
- https://github.com/pterodactyl/panel/commit/092e7e79fff858ee026608c7dbccab165a67526f
- https://github.com/pterodactyl/panel
- https://github.com/pterodactyl/panel/releases/tag/v0.7.14
