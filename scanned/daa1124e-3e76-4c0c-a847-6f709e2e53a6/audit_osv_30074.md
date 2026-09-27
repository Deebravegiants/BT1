# [H] ext4: fix timer use-after-free on failed mount

## Summary
Severity: High
Advisory: CVE-2024-49960
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49960
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.237, >=5.11.0 <5.15.181, >=5.14.0 <6.1.118, >=5.16.0 <6.6.55, >=6.2.0 <6.10.14, >=6.7.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ext4: fix timer use-after-free on failed mount

Syzbot has found an ODEBUG bug in ext4_fill_super

The del_timer_sync function cancels the s_err_report timer,
which reminds about filesystem errors daily. We should
guarantee the timer is no longer active before kfree(sbi).

When filesystem mounting fails, the flow goes to failed_mount3,
where an error occurs when ext4_stop_mmpd is called, causing
a read I/O failure. This triggers the ext4_handle_error function
that ultimately re-arms the timer,
leaving the s_err_report timer active before kfree(sbi) is called.

Fix the issue by canceling the s_err_report timer after calling ext4_stop_mmpd.

## References
- https://git.kernel.org/stable/c/0ce160c5bdb67081a62293028dc85758a8efb22a
- https://git.kernel.org/stable/c/22e9b83f0f33bc5a7a3181769d1dccbf021f5b04
- https://git.kernel.org/stable/c/7aac0c17a8cdf4a3236991c1e60435c6a984076c
- https://git.kernel.org/stable/c/9203817ba46ebba7c865c8de2aba399537b6e891
- https://git.kernel.org/stable/c/b85569585d0154d4db1e4f9e3e6a4731d407feb0
- https://git.kernel.org/stable/c/cf3196e5e2f36cd80dab91ffae402e13935724bc
- https://git.kernel.org/stable/c/fa78fb51d396f4f2f80f8e96a3b1516f394258be
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49960.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49960
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
