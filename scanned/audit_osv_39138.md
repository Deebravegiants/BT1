# [C] Cleanuparr: X-Forwarded-For leftmost parsing allows remote unauthenticated admin takeover when reverse-proxy mode is enabled

## Summary
Severity: Critical
Advisory: CVE-2026-44183
Aliases: GHSA-8q44-v65j-jc3q
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44183
Type: osv

## Details
Cleanuparr is a tool for automating the cleanup of unwanted or blocked files in Sonarr, Radarr, and supported download clients like qBittorrent.  Prior to 2.9.10, TrustedNetworkAuthenticationHandler.ResolveClientIp parses the leftmost entry of the X-Forwarded-For header as the client IP. That entry is attacker-controlled — X-Forwarded-For is append-only, so the leftmost value is whatever the original HTTP client claimed. By sending a spoofed local IP in the header, an unauthenticated remote attacker passes the trusted-network check and is logged in as the Cleanuparr administrator. This vulnerability is fixed in 2.9.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44183.json
- https://github.com/Cleanuparr/Cleanuparr/security/advisories/GHSA-8q44-v65j-jc3q
- https://nvd.nist.gov/vuln/detail/CVE-2026-44183
