# [H] btrfs: don't clobber ret in btrfs_validate_super()

## Summary
Severity: High
Advisory: CVE-2025-22114
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22114
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

btrfs: don't clobber ret in btrfs_validate_super()

Commit 2a9bb78cfd36 ("btrfs: validate system chunk array at
btrfs_validate_super()") introduces a call to validate_sys_chunk_array()
in btrfs_validate_super(), which clobbers the value of ret set earlier.
This has the effect of negating the validity checks done earlier, making
it so btrfs could potentially try to mount invalid filesystems.

## References
- https://git.kernel.org/stable/c/9db9c7dd5b4e1d3205137a094805980082c37716
- https://git.kernel.org/stable/c/ef6800a2015e706e9852a5ec15263fec9990d012
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22114.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22114
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
