# [M] ApostropheCMS: Missing destination-parent authorization in page `move()` allows a low-privileged editor to move and re-rank pages inside a restricted subtree

## Summary
Severity: Medium
Advisory: CVE-2026-63669
Aliases: GHSA-wr5r-wqp2-x4fh
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-63669
Type: osv

## Details
ApostropheCMS is an open-source Node.js content management system. Prior to 4.32.0, the page module's move() operation fails to enforce the destination parent's _create permission because its oldParent archive condition disables the check for ordinary moves, allowing an authenticated editor or contributor to use _targetId and _position through the page REST update endpoint to move a controlled page into a restricted subtree and make nudgeNewPeers() updateMany re-rank protected sibling pages. This issue is fixed in version 4.32.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63669.json
- https://github.com/apostrophecms/apostrophe/security/advisories/GHSA-wr5r-wqp2-x4fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-63669
- https://github.com/apostrophecms/apostrophe/commit/d50c6ad61b9c1788958752358f1fca714cc8368c
