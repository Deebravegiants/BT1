# [M] rsync < 3.5.0 Symlink Race Condition Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-53797
Aliases: GHSA-3jj3-qvc7-jp6x
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53797
Type: osv

## Details
rsync before 3.5.0 contains a symlink race condition vulnerability in the sender's source tree traversal that allows an attacker who can manipulate a parent directory of the source tree to redirect file reads to unintended paths. Attackers can atomically replace a parent directory component with a symlink pointing outside the source root between path resolution and file open operations to disclose file contents outside the intended transfer root.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53797.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-3jj3-qvc7-jp6x
- https://nvd.nist.gov/vuln/detail/CVE-2026-53797
- https://www.vulncheck.com/advisories/rsync-symlink-race-condition-information-disclosure
- https://github.com/RsyncProject/rsync
