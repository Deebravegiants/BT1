# [H] Cleanuparr: Reflective CORS combined with trusted-network auth allows cross-origin admin API reads

## Summary
Severity: High
Advisory: CVE-2026-44184
Aliases: GHSA-rwpc-36mg-fpvf
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44184
Type: osv

## Details
Cleanuparr is a tool for automating the cleanup of unwanted or blocked files in Sonarr, Radarr, and supported download clients like qBittorrent.  Prior to 2.9.10, Cleanuparr's global CORS policy reflects every request Origin and combines it with AllowCredentials(). When DisableAuthForLocalAddresses is enabled, the API also authenticates requests purely by source IP via TrustedNetworkAuthenticationHandler. The combination lets any website that an admin (or any user on a trusted IP) visits read authenticated API responses cross-origin — including the admin's permanent API key. This vulnerability is fixed in 2.9.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44184.json
- https://github.com/Cleanuparr/Cleanuparr/security/advisories/GHSA-rwpc-36mg-fpvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-44184
