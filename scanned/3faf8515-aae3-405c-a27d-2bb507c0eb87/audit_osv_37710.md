# [C] Anchorr Privilege Escalation: Jellyseerr User → Anchorr Admin via Stored XSS

## Summary
Severity: Critical
Advisory: CVE-2026-32891
Aliases: GHSA-6mg4-788h-7g9g
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-32891
Type: osv

## Details
Anchorr is a Discord bot for requesting movies and TV shows and receiving notifications when items are added to a media server. Versions 1.4.1 and below contain a stored XSS vulnerability in the Jellyseerr user selector. Jellyseerr allows any account holder to execute arbitrary JavaScript in the Anchorr admin's browser session. The injected script calls the authenticated /api/config endpoint - which returns the full application configuration in plaintext. This allows the attacker to forge a valid Anchorr session token and gain full admin access to the dashboard with no knowledge of the admin password. The same response also exposes the API keys and tokens for every integrated service, resulting in simultaneous account takeover of the Jellyfin media server (via JELLYFIN_API_KEY), the Jellyseerr request manager (via JELLYSEERR_API_KEY), and the Discord bot (via DISCORD_TOKEN). This issue has been fixed in version 1.4.2.

## References
- https://github.com/openVESSL/Anchorr/releases/tag/v1.4.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32891.json
- https://github.com/openVESSL/Anchorr/security/advisories/GHSA-6mg4-788h-7g9g
- https://nvd.nist.gov/vuln/detail/CVE-2026-32891
