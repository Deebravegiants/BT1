# [H] jfs: fix uaf in jfs_evict_inode

## Summary
Severity: High
Advisory: CVE-2023-52600
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52600
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.19.307, >=4.20.0 <5.4.269, >=5.5.0 <5.10.210, >=5.11.0 <5.15.149, >=5.16.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

jfs: fix uaf in jfs_evict_inode

When the execution of diMount(ipimap) fails, the object ipimap that has been
released may be accessed in diFreeSpecial(). Asynchronous ipimap release occurs
when rcu_core() calls jfs_free_node().

Therefore, when diMount(ipimap) fails, sbi->ipimap should not be initialized as
ipimap.

## References
- https://git.kernel.org/stable/c/1696d6d7d4a1b373e96428d0fe1166bd7c3c795e
- https://git.kernel.org/stable/c/32e8f2d95528d45828c613417cb2827d866cbdce
- https://git.kernel.org/stable/c/81b4249ef37297fb17ba102a524039a05c6c5d35
- https://git.kernel.org/stable/c/8e44dc3f96e903815dab1d74fff8faafdc6feb61
- https://git.kernel.org/stable/c/93df0a2a0b3cde2d7ab3a52ed46ea1d6d4aaba5f
- https://git.kernel.org/stable/c/bacdaa04251382d7efd4f09f9a0686bfcc297e2e
- https://git.kernel.org/stable/c/bc6ef64dbe71136f327d63b2b9071b828af2c2a8
- https://git.kernel.org/stable/c/e0e1958f4c365e380b17ccb35617345b31ef7bf3
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52600.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52600
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
