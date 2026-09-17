# [C] ntfs: harden runlist realloc size calculations

## Summary
Severity: Critical
Advisory: CVE-2026-74570
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74570
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ntfs: harden runlist realloc size calculations

Add a shared helper to safely convert runlist element counts to byte sizes
using overflow checks, and use it in both ntfs_rl_realloc() and
ntfs_rl_realloc_nofail().

## References
- https://git.kernel.org/stable/c/57e7b8bf7b02a0140463fea786e5172cbdf2da2f
- https://git.kernel.org/stable/c/8bed376124ab4505b70083a2b91f2c7ef6d51e24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74570.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74570
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
