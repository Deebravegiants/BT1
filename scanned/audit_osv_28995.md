# [H] nilfs2: fix use-after-free of timer for log writer thread

## Summary
Severity: High
Advisory: CVE-2024-38583
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38583
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.94, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nilfs2: fix use-after-free of timer for log writer thread

Patch series "nilfs2: fix log writer related issues".

This bug fix series covers three nilfs2 log writer-related issues,
including a timer use-after-free issue and potential deadlock issue on
unmount, and a potential freeze issue in event synchronization found
during their analysis.  Details are described in each commit log.


This patch (of 3):

A use-after-free issue has been reported regarding the timer sc_timer on
the nilfs_sc_info structure.

The problem is that even though it is used to wake up a sleeping log
writer thread, sc_timer is not shut down until the nilfs_sc_info structure
is about to be freed, and is used regardless of the thread's lifetime.

Fix this issue by limiting the use of sc_timer only while the log writer
thread is alive.

## References
- https://git.kernel.org/stable/c/2f12b2c03c5dae1a0de0a9e5853177e3d6eee3c6
- https://git.kernel.org/stable/c/67fa90d4a2ccd9ebb0e1e168c7d0b5d0cf3c7148
- https://git.kernel.org/stable/c/68e738be5c518fc3c4e9146b66f67c8fee0135fb
- https://git.kernel.org/stable/c/822ae5a8eac30478578a75f7e064f0584931bf2d
- https://git.kernel.org/stable/c/82933c84f188dcfe89eb26b0b48ab5d1ca99d164
- https://git.kernel.org/stable/c/86a30d6302deddb9fb97ba6fc4b04d0e870b582a
- https://git.kernel.org/stable/c/e65ccf3a4de4f0c763d94789615b83e11f204438
- https://git.kernel.org/stable/c/f5d4e04634c9cf68bdf23de08ada0bb92e8befe7
- https://git.kernel.org/stable/c/f9186bba4ea282b07293c1c892441df3a5441cb0
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38583.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38583
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
