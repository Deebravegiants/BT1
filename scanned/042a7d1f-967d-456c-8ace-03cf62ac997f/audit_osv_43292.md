# [C] PeerTube: Unauthenticated remote SQL injection in ActorFollowModel.updateScore()

## Summary
Severity: Critical
Advisory: CVE-2026-73211
Aliases: GHSA-pqr4-34h8-g39x
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73211
Type: osv

## Details
PeerTube is an ActivityPub-federated video streaming platform. Prior to 8.1.6, ActorFollowModel.updateScore() interpolates the attacker-controlled ActivityPub actor inboxUrl into an SQL query, allowing an unauthenticated remote server to read and write PeerTube database tables, including oAuthToken.accessToken, and take over administrator accounts. This issue is fixed in version 8.1.6.

## References
- https://github.com/Chocobozzz/PeerTube/releases/tag/v8.1.6
- https://github.com/Chocobozzz/PeerTube/releases/tag/v8.1.8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73211.json
- https://github.com/Chocobozzz/PeerTube/security/advisories/GHSA-pqr4-34h8-g39x
- https://nvd.nist.gov/vuln/detail/CVE-2026-73211
- https://github.com/Chocobozzz/PeerTube/commit/cc07364a5d635b6e43a92fc5e2e2e3eeacf4e8f4
