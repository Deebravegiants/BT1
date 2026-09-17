# [M] rsync < 3.5.0 Symlink Race Condition Directory Traversal

## Summary
Severity: Medium
Advisory: CVE-2026-53801
Aliases: GHSA-mch3-qr4p-chgm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53801
Type: osv

## Details
rsync before 3.5.0 contains a symlink race condition vulnerability in the sender's directory scanning logic that allows attackers to cause the sender to enumerate and transfer files outside the module root's intended subtree. Attackers who can create or manipulate symlinks in a path component of the scanned tree can replace a symlink with a directory entry pointing outside the module root between the lstat() call and the subsequent opendir() call, exposing files beyond the intended root in both daemon-mode and non-daemon sender-side scanning.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53801.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-mch3-qr4p-chgm
- https://nvd.nist.gov/vuln/detail/CVE-2026-53801
- https://www.vulncheck.com/advisories/rsync-symlink-race-condition-directory-traversal
- https://github.com/RsyncProject/rsync
