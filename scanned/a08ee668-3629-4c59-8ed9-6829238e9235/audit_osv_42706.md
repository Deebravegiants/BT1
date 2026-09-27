# [C] rsync 2.3.3 < 3.5.0 Path Traversal via --partial-dir/--backup-dir Symlink

## Summary
Severity: Critical
Advisory: CVE-2026-70460
Aliases: GHSA-w3xf-j2r2-gv4x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-70460
Type: osv

## Details
rsync 2.3.3 before 3.5.0 contains a path traversal vulnerability that allows a malicious sender to escape the module root by exploiting symlinks within the module file tree when using --partial-dir or --backup-dir options. Attackers with write access to place a symlink under the module root, or who can exploit a pre-existing trusted symlink, can direct file writes to locations outside the intended module root, achieving arbitrary file write relative to the module root parent.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70460.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-w3xf-j2r2-gv4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-70460
- https://www.vulncheck.com/advisories/rsync-path-traversal-via-partial-dir-backup-dir-symlink
- https://github.com/RsyncProject/rsync
