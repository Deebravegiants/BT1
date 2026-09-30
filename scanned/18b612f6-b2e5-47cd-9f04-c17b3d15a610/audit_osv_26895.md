# [M] PocketMine-MP before 5.3.1 Denial of Service via LoginPacket

## Summary
Severity: Medium
Advisory: CVE-2023-54390
Aliases: GHSA-92jh-gwch-jq38
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2023-54390
Type: osv

## Details
PocketMine-MP versions before 5.3.1 and 4.23.1 contain a denial of service vulnerability in LoginPacket JSON parsing due to improper null value handling in arrays. Attackers can send malformed JSON with unexpected null elements in LoginPacket to crash the server.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54390.json
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-92jh-gwch-jq38
- https://nvd.nist.gov/vuln/detail/CVE-2023-54390
- https://www.vulncheck.com/advisories/pocketmine-mp-before-5.3.1-denial-of-service-via-loginpacket
- https://github.com/pmmp/PocketMine-MP/commit/4f90e8dab1c9df331fad7d3d89823404e882668c
