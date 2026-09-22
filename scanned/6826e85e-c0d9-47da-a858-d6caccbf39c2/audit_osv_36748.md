# [M] WeKan < 8.19 Cross-board Card Move Without Destination Authorization

## Summary
Severity: Medium
Advisory: CVE-2026-25566
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-07
Source: https://osv.dev/vulnerability/CVE-2026-25566
Type: osv

## Details
WeKan versions prior to 8.19 contain an authorization vulnerability in card move logic. A user can specify a destination board/list/swimlane without adequate authorization checks for the destination and without validating that destination objects belong to the destination board, potentially enabling unauthorized cross-board moves.

## References
- https://wekan.fi/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25566.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25566
- https://www.vulncheck.com/advisories/wekan-cross-board-card-move-without-destination-authorization
- https://github.com/wekan/wekan/commit/198509e7600981400353aec6259247b3c04e043e
- https://github.com/wekan/wekan
