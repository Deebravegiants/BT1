# [C] PeerTube: Cross-origin remote video takeover via Update activity

## Summary
Severity: Critical
Advisory: CVE-2026-73090
Aliases: GHSA-g9p4-f7h8-hc86
CVSS: 9.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:N)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/CVE-2026-73090
Type: osv

## Details
PeerTube is an ActivityPub-federated video streaming platform. Prior to 8.2.2, processUpdateActivity and processUpdateVideo accept an ActivityPub Update containing a Video object without verifying that byActor.url is authorized for the host in videoObject.id, allowing a malicious federated server to rewrite another server's video metadata, visibility, media file, and HLS URLs. This issue is fixed in version 8.2.2.

## References
- https://github.com/Chocobozzz/PeerTube/releases/tag/v8.2.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73090.json
- https://github.com/Chocobozzz/PeerTube/security/advisories/GHSA-g9p4-f7h8-hc86
- https://nvd.nist.gov/vuln/detail/CVE-2026-73090
- https://github.com/Chocobozzz/PeerTube/commit/63d487d2a4a2a0e36af8c0ccb888cd23725bf7f2
