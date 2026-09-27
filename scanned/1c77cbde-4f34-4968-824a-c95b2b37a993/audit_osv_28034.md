# [M] f2fs: fix to avoid potential panic during recovery

## Summary
Severity: Medium
Advisory: CVE-2024-27032
Ecosystem: Linux
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27032
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to avoid potential panic during recovery

During recovery, if FAULT_BLOCK is on, it is possible that
f2fs_reserve_new_block() will return -ENOSPC during recovery,
then it may trigger panic.

Also, if fault injection rate is 1 and only FAULT_BLOCK fault
type is on, it may encounter deadloop in loop of block reservation.

Let's change as below to fix these issues:
- remove bug_on() to avoid panic.
- limit the loop count of block reservation to avoid potential
deadloop.

## References
- https://git.kernel.org/stable/c/21ec68234826b1b54ab980a8df6e33c74cfbee58
- https://git.kernel.org/stable/c/8844b2f8a3f0c428b74672f9726f9950b1a7764c
- https://git.kernel.org/stable/c/d034810d02a5af8eb74debe29877dcaf5f00fdd1
- https://git.kernel.org/stable/c/f26091a981318b5b7451d61f99bc073a6af8db67
- https://git.kernel.org/stable/c/fe4de493572a4263554903bf9c3afc5c196e15f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27032.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27032
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
