# [M] Jellyfin Web Cross-Site Scripting (XSS) via Playlist Name

## Summary
Severity: Medium
Advisory: GHSA-2h5r-cqfc-45v6
CVE: CVE-2023-23636
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-02-03
Source: https://github.com/advisories/GHSA-2h5r-cqfc-45v6
Type: github-advisory

## Affected
- npm: `jellyfin-web` — affected >=10.8.0 <10.8.4

## Details
In Jellyfin 10.8.x through 10.8.3, the name of a playlist is vulnerable to stored XSS. This allows an attacker to steal access tokens from the localStorage of the victim.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-23636
- https://github.com/jellyfin/jellyfin-web/issues/3788
- https://github.com/jellyfin/jellyfin-web/pull/3789
- https://github.com/jellyfin/jellyfin-web
- https://github.com/jellyfin/jellyfin/releases/tag/v10.8.4
- https://herolab.usd.de/security-advisories
- https://herolab.usd.de/security-advisories/usd-2022-0030
