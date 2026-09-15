# [M] rsync < 3.5.0 Symlink Race Condition via --remove-source-files

## Summary
Severity: Medium
Advisory: CVE-2026-53800
Aliases: GHSA-v3vw-pvpg-chwh
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-53800
Type: osv

## Details
rsync before 3.5.0 contains a symlink race condition vulnerability in the --remove-source-files feature that allows attackers with symlink creation access to cause arbitrary file deletion. Attackers can atomically substitute a symlink for a source file between transfer completion and the unlink() call, causing rsync to delete the symlink target rather than the intended source file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53800.json
- https://github.com/RsyncProject/rsync/releases/tag/v3.5.0
- https://github.com/RsyncProject/rsync/security/advisories/GHSA-v3vw-pvpg-chwh
- https://nvd.nist.gov/vuln/detail/CVE-2026-53800
- https://www.vulncheck.com/advisories/rsync-symlink-race-condition-via-remove-source-files
- https://github.com/RsyncProject/rsync
