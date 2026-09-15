# [H] PeerTube ActivityPub Playlist Creation Blind SSRF and DoS

## Summary
Severity: High
Advisory: CVE-2025-32948
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32948
Type: osv

## Details
The vulnerability allows any attacker to cause the PeerTube server to stop functioning, or in special cases send requests to arbitrary URLs (Blind SSRF). Attackers can send ActivityPub activities to PeerTube's "inbox" endpoint. By abusing the "Create Activity" functionality, it is possible to create crafted playlists which will cause either denial of service or an attacker-controlled blind SSRF.

## References
- https://github.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32948.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32948
- https://research.jfrog.com/vulnerabilities/peertube-activitypub-playlist-creation-blind-ssrf-dos/
- https://github.com/Chocobozzz/PeerTube/releases/tag/v7.1.1
