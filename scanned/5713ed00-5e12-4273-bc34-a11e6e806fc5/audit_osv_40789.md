# [M] NILFS utilities - Undefined Behavior and Out-of-Memory via Unvalidated s_log_block_size

## Summary
Severity: Medium
Advisory: CVE-2026-55392
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/CVE-2026-55392
Type: osv

## Details
NILFS utilities through 2.3.0, fixed in commit 26efb5d, nilfs_sb_is_valid() function fails to validate s_log_block_size field in NILFS2 superblock before bit-shift operations. Attackers supplying crafted NILFS2 images trigger undefined behavior through oversized shifts or out-of-memory conditions, crashing tools like nilfs-tune and dumpseg.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55392.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55392
- https://github.com/nilfs-dev/nilfs-utils/issues/26
- https://github.com/nilfs-dev/nilfs-utils/commit/26efb5daff0757365101035145331b0a5a85d9d9
- https://github.com/nilfs-dev/nilfs-utils
