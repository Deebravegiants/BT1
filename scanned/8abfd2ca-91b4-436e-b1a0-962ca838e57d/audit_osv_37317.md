# [H] Sonarr Path Traversal vulnerability

## Summary
Severity: High
Advisory: CVE-2026-30976
Aliases: GHSA-h393-v5hm-6h8f
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-30976
Type: osv

## Details
Sonarr is a PVR for Usenet and BitTorrent users. In versions on the 4.x branch prior to 4.0.17.2950, an unauthenticated remote attacker can potentially read any file readable by the Sonarr process. These include application configuration files (containing API keys and database credentials), Windows system files, and any user-accessible files on the same drive This issue only impacts Windows systems; macOS and Linux are unaffected. Files returned from the API were not limited to the directory on disk they were intended to be served from. This problem has been patched in 4.0.17.2950 in the nightly/develop branch or 4.0.17.2952 for stable/main releases. It's possible to work around the issue by only hosting Sonarr on a secure internal network and accessing it via VPN, Tailscale or similar solution outside that network.

## References
- https://github.com/Sonarr/Sonarr/releases/tag/v4.0.17.2950
- https://github.com/Sonarr/Sonarr/releases/tag/v4.0.17.2952
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/30xxx/CVE-2026-30976.json
- https://github.com/Sonarr/Sonarr/security/advisories/GHSA-h393-v5hm-6h8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-30976
