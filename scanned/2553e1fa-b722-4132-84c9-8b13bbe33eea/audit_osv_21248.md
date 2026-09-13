# [M] CVE-2021-41324

## Summary
Severity: Medium
Advisory: CVE-2021-41324
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-09-30
Source: https://osv.dev/vulnerability/CVE-2021-41324
Type: osv

## Details
Directory traversal in the Copy, Move, and Delete features in Pydio Cells 2.2.9 allows remote authenticated users to enumerate personal files (or Cells files belonging to any user) via the nodes parameter (for Copy and Move) or via the Path parameter (for Delete).

## References
- https://charonv.net/Pydio-Broken-Access-Control/
- https://github.com/pydio/cells/releases/tag/v2.2.12
- https://pydio.com/fr/community/releases/pydio-cells/pydio-cells-enterprise-2212
