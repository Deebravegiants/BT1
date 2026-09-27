# [H] rsync < 3.5.0 Path Traversal Write Escape via --relative Mode

## Summary
Severity: High
Advisory: CVE-2026-53785
Aliases: GHSA-pph3-7xmf-rrqg
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53785
Type: osv

## Details
rsync before 3.5.0 contains a path traversal vulnerability that allows a malicious sender to write files outside the intended destination directory tree by crafting relative paths with symlink components in --relative mode. The make_path() function follows symlinks pointing outside the destination tree while creating intermediate directories without verifying that created paths remain within the destination boundary, enabling arbitrary file writes on the receiver's filesystem.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53785.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-pph3-7xmf-rrqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-53785
- https://www.vulncheck.com/advisories/rsync-path-traversal-write-escape-via-relative-mode
- https://github.com/RsyncProject/rsync
