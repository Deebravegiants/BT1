# [M] Jellyfin Vulnerable to Denial of Service (DoS) via IP Spoofing

## Summary
Severity: Medium
Advisory: CVE-2025-32012
Aliases: GHSA-qcmf-gmhm-rfv9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32012
Type: osv

## Details
Jellyfin is an open source self hosted media server. In versions 10.9.0 to before 10.10.7, the /System/Restart endpoint provides administrators the ability to restart their Jellyfin server. This endpoint is intended to be admins-only, but it also authorizes requests from any device in the same local network as the Jellyfin server. Due to the method Jellyfin uses to determine the source IP of a request, an unauthenticated attacker is able to spoof their IP to appear as a LAN IP, allowing them to restart the Jellyfin server process without authentication. This means that an unauthenticated attacker could mount a denial-of-service attack on any default-configured Jellyfin server by simply sending the same spoofed request every few seconds to restart the server over and over. This method of IP spoofing also bypasses some security mechanisms, cause a denial-of-service attack, and possible bypass the admin restart requirement if combined with remote code execution. This issue is patched in version 10.10.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32012.json
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-qcmf-gmhm-rfv9
- https://nvd.nist.gov/vuln/detail/CVE-2025-32012
- https://github.com/jellyfin/jellyfin/commit/f625665cb116a7e3feb8b79aaf1ed39a956e0585
