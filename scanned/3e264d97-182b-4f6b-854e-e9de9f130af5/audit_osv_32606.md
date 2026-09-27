# [M] PeerTube Arbitrary Playlist Creation via REST API

## Summary
Severity: Medium
Advisory: CVE-2025-32945
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32945
Type: osv

## Details
The vulnerability allows an existing user to add playlists to a different user’s channel using the PeerTube REST API. The vulnerable code sets the owner of the new playlist to be the user who performed the request, and then sets the associated channel to the channel ID supplied by the request, without checking if it belongs to the user.

## References
- https://github.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32945.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32945
- https://research.jfrog.com/vulnerabilities/peertube-arbitrary-playlist-creation-rest/
- https://github.com/Chocobozzz/PeerTube/releases/tag/v7.1.1
