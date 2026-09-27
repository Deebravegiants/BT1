# [M] gitoxide before 0.33.0 Path Traversal via symlink following

## Summary
Severity: Medium
Advisory: CVE-2026-82248
Aliases: GHSA-pmm9-4h7q-24c8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82248
Type: osv

## Details
gix-worktree-state before 0.33.0 (part of gitoxide) allows writing files outside the worktree on Windows. gix_worktree_state::checkout() follows an existing terminal symlink during non-exclusive (incremental) materialization (destination_is_initially_empty: false) when core.symlinks is true. If a symlink entry (mode 120000) is first checked out at a path P pointing outside the worktree, a subsequent incremental checkout of a regular-file entry (mode 100644) at the same path follows the existing reparse point and writes the blob content through the link, overwriting files outside the worktree.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82248.json
- https://github.com/GitoxideLabs/gitoxide/security/advisories/GHSA-pmm9-4h7q-24c8
- https://nvd.nist.gov/vuln/detail/CVE-2026-82248
- https://www.vulncheck.com/advisories/gitoxide-before-0.33.0-path-traversal-via-symlink-following
