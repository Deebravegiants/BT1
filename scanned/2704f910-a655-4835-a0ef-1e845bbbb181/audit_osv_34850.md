# [M] CVE-2025-65782

## Summary
Severity: Medium
Advisory: CVE-2025-65782
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-65782
Type: osv

## Details
An issue was discovered in Wekan The Open Source kanban board system up to version 18.15, fixed in 18.16. Authorization flaw in card update handling allows board members (and potentially other authenticated users) to add/remove arbitrary user IDs in vote.positive / vote.negative arrays, enabling vote forgery and unauthorized voting.

## References
- https://github.com/wekan/wekan/blob/main/CHANGELOG.md#v816-2025-11-02-wekan--release
- https://wekan.fi/hall-of-fame/spacebleed/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65782.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-65782
- https://github.com/wekan/wekan/commit/0a1a075f3153e71d9a858576f1c68d2925230d9c
- https://github.com/wekan/wekan
