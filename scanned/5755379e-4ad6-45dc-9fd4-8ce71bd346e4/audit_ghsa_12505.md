# [M] Maloja error page XSS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4h72-34j6-j8x7
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-12-18
Source: https://github.com/advisories/GHSA-4h72-34j6-j8x7
Type: github-advisory

## Affected
- PyPI: `malojaserver` — affected >=0 <3.2.2

## Details
### Impact
The error page for a missing path echoes the path back to the user. If this contains HTML, an attacker could execute a script on the user's machine inside the Maloja context and perform authorized actions like scrobbling or deleting scrobbles.
This does not affect the security of your server. The exploit is purely client-side.
Since there is very little incentive to mess with your scrobble data and it requires very specific targeting (an attacker would have to send a user a link to their own server),  the severity rating might be misleading.

### Patches
The Vulnerability is patched in 3.2.2

## References
- https://github.com/krateng/maloja/security/advisories/GHSA-4h72-34j6-j8x7
- https://github.com/krateng/maloja/commit/febaff97228b37a192f2630aa331cac5e5c3e98e
- https://github.com/krateng/maloja
