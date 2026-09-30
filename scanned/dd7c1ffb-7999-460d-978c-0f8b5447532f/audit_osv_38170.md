# [M] Jellyfin: Potential Application DoS from excessively large SyncPlay group names

## Summary
Severity: Medium
Advisory: CVE-2026-35034
Aliases: GHSA-v2jv-54xj-h76w
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-35034
Type: osv

## Details
Jellyfin is an open source self hosted media server. Versions prior to 10.11.7 contain a denial of service vulnerability in the SyncPlay group creation endpoint (POST /SyncPlay/New), where an authenticated user can create groups with names of unlimited size due to insufficient input validation. By sending large payloads combined with arbitrary group IDs, an attacker can lock out the endpoint for other clients attempting to join SyncPlay groups and significantly increase the memory usage of the Jellyfin process, potentially leading to an out-of-memory crash. This issue has been fixed in version 10.11.7.

## References
- https://github.com/jellyfin/jellyfin/releases/tag/v10.11.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35034.json
- https://github.com/jellyfin/jellyfin/security/advisories/GHSA-v2jv-54xj-h76w
- https://nvd.nist.gov/vuln/detail/CVE-2026-35034
