# [H] Cinny vulnerable to access token disclosure via invalidated emoji pack avatar URL in service worker

## Summary
Severity: High
Advisory: GHSA-j944-w549-3453
CVE: CVE-2026-42553
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-j944-w549-3453
Type: github-advisory

## Affected
- npm: `cinny` — affected >=0 <4.10.3

## Details
### Impact
A remote authenticated attacker who shares a room with a victim and has permissions to create room emotes (for example in a DM) can cause the victim's client to send their Matrix access token to an attacker-controlled server. This occurs when the victim opens the emoji or sticker picker for the room containing a malicious emote pack. 

The root causes are: 

(1) an incorrect fallback in EmojiBoard that uses untrusted `pack.meta.avatar` (user-controlled) without converting/validating it as an MXC URL, allowing arbitrary HTTP(S) URLs to be used; and 

(2) the service worker attaching the user's Authorization bearer token to all outbound GET requests whose URL contains `/_matrix/client/v1/media/download` or `/_matrix/client/v1/media/thumbnail` without verifying the request host matches the configured homeserver origin. An attacker-controlled URL containing those path fragments and permissive CORS will receive the victim's Authorization header (access token). 

Impacted users: anybody using affected Cinny web app versions who opens the emoji/sticker picker in a room containing a malicious emote pack and who is logged in (authenticated).

### Patches
Version with fixes: https://github.com/cinnyapp/cinny/releases/tag/v4.10.3

## References
- https://github.com/cinnyapp/cinny/security/advisories/GHSA-j944-w549-3453
- https://nvd.nist.gov/vuln/detail/CVE-2026-42553
- https://github.com/cinnyapp/cinny
- https://github.com/cinnyapp/cinny/releases/tag/v4.10.3
