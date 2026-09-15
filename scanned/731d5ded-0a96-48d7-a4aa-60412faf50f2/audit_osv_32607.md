# [M] PeerTube Arbitrary Playlist Creation via ActivityPub Protocol

## Summary
Severity: Medium
Advisory: CVE-2025-32946
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32946
Type: osv

## Details
This vulnerability allows any attacker to add playlists to a different user’s channel using the ActivityPub protocol. The vulnerable code sets the owner of the new playlist to be the user who performed the request, and then sets the associated channel to the channel ID supplied by the request, without checking if it belongs to the user.

## References
- https://github.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32946.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-32946
- https://research.jfrog.com/vulnerabilities/peertube-arbitrary-playlist-creation-activitypub/
- https://github.com/Chocobozzz/PeerTube/releases/tag/v7.1.1
