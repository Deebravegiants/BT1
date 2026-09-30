# [M] ClipBucket v5 enables internal network scans via an SSRF vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-26005
Aliases: GHSA-69xj-2pq3-5r4v
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-02-12
Source: https://osv.dev/vulnerability/CVE-2026-26005
Type: osv

## Details
ClipBucket v5 is an open source video sharing platform. Prior to 5.5.3 - #45, in Clip Bucket V5, The Remote Play allows creating video entries that reference external video URLs without uploading the video files to the server. However, by specifying an internal network host in the video URL, an SSRF can be triggered, causing GET requests to be sent to internal servers. An attacker can exploit this to scan the internal network. Even a regular (non-privileged) user can carry out the attack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26005.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-69xj-2pq3-5r4v
- https://nvd.nist.gov/vuln/detail/CVE-2026-26005
- https://github.com/MacWarrior/clipbucket-v5/commit/a9e0f2322fb37501dfd4f44079fc7826a132503a
