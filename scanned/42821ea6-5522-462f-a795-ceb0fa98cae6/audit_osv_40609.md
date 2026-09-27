# [H] rsync < 3.5.0 Path Traversal via Symlink Module Root

## Summary
Severity: High
Advisory: CVE-2026-53784
Aliases: GHSA-ffg2-fr5g-3rxw
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53784
Type: osv

## Details
rsync before 3.5.0 contains a path traversal vulnerability that allows remote clients to access files outside the intended module root when use chroot is disabled and the module root path or a component of it is a symlink. The daemon calls chdir() to the module root at session initialization without resolving symlinks via realpath() or equivalent, causing subsequent relative-path operations to reference files relative to the symlink target rather than the intended module root, enabling unauthorized file access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53784.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-ffg2-fr5g-3rxw
- https://nvd.nist.gov/vuln/detail/CVE-2026-53784
- https://www.vulncheck.com/advisories/rsync-path-traversal-via-symlink-module-root
- https://github.com/RsyncProject/rsync
