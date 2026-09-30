# [H] CVE-2025-65779

## Summary
Severity: High
Advisory: CVE-2025-65779
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-65779
Type: osv

## Details
An issue was discovered in Wekan The Open Source kanban board system up to version 18.15, fixed in 18.16. Unauthenticated attackers can update a board's "sort" value (Boards.allow returns true without verifying userId), allowing arbitrary reordering of boards.

## References
- https://github.com/wekan/wekan/blob/main/CHANGELOG.md#v816-2025-11-02-wekan--release
- https://wekan.fi/hall-of-fame/spacebleed/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65779.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65779
- https://github.com/wekan/wekan/commit/ea310d7508b344512e5de0dfbc9bdfd38145c5c5
- https://github.com/wekan/wekan
