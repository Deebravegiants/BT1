# [M] Pterodactyl TOTPs can be reused during validity window

## Summary
Severity: Medium
Advisory: GHSA-rgmp-4873-r683
CVE: CVE-2025-69197
CWE: CWE-287
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-06
Source: https://github.com/advisories/GHSA-rgmp-4873-r683
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.12.0

## Details
### Summary
When a user signs into an account with 2FA enabled they are prompted to enter a token. When that token is used, it is not sufficiently marked as used in the system allowing an attacker that intercepts that token to then use it in addition to a known username/password during the token validity window.

This vulnerability requires that an attacker already be in possession of a valid username and password combination, and intercept a valid 2FA token (for example, during a screen share). The token must then be provided in addition to the username and password during the limited token validity window. The validity window is ~60 seconds as the Panel allows at most one additional window to the current one, each window being 30 seconds.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-rgmp-4873-r683
- https://nvd.nist.gov/vuln/detail/CVE-2025-69197
- https://github.com/pterodactyl/panel/commit/032bf076d92bb2f929fa69c1bac1b89f26b8badf
- https://github.com/pterodactyl/panel
- https://github.com/pterodactyl/panel/releases/tag/v1.12.0
