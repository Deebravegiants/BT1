# [H] Plex-configured Seerr instances vulnerable to unauthenticated account registration via Jellyfin authentication endpoint

## Summary
Severity: High
Advisory: CVE-2026-27707
Aliases: GHSA-rc4w-7m3r-c2f7
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-02-27
Source: https://osv.dev/vulnerability/CVE-2026-27707
Type: osv

## Details
Seerr is an open-source media request and discovery manager for Jellyfin, Plex, and Emby. Starting in version 2.0.0 and prior to version 3.1.0, an authentication guard logic flaw in `POST /api/v1/auth/jellyfin` allows an unauthenticated attacker to register a new Seerr account on any Plex-configured instance by authenticating with an attacker-controlled Jellyfin server. The attacker receives an authenticated session and can immediately use the application with default permissions, including the ability to submit media requests to Radarr/Sonarr. Any Seerr deployment where all three of the following are true may be vulnerable: `settings.main.mediaServerType` is set to `PLEX` (the most common deployment).; `settings.jellyfin.ip` is set to `""` (default, meaning Jellyfin was never configured); and `settings.main.newPlexLogin` is set to `true` (default). Jellyfin-configured and Emby-configured deployments are not affected. Version 3.1.0 of Seerr fixes this issue.

## References
- https://github.com/seerr-team/seerr/releases/tag/v3.1.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27707.json
- https://github.com/seerr-team/seerr/security/advisories/GHSA-rc4w-7m3r-c2f7
- https://nvd.nist.gov/vuln/detail/CVE-2026-27707
- https://github.com/seerr-team/seerr/commit/4ae20684092b5b28527b23dfbc1a3417858fee8e
