# [H] xen: privcmd: Fix possible access to a freed kirqfd instance

## Summary
Severity: High
Advisory: CVE-2024-46762
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-18
Source: https://osv.dev/vulnerability/CVE-2024-46762
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.51, >=6.7.0 <6.10.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

xen: privcmd: Fix possible access to a freed kirqfd instance

Nothing prevents simultaneous ioctl calls to privcmd_irqfd_assign() and
privcmd_irqfd_deassign(). If that happens, it is possible that a kirqfd
created and added to the irqfds_list by privcmd_irqfd_assign() may get
removed by another thread executing privcmd_irqfd_deassign(), while the
former is still using it after dropping the locks.

This can lead to a situation where an already freed kirqfd instance may
be accessed and cause kernel oops.

Use SRCU locking to prevent the same, as is done for the KVM
implementation for irqfds.

## References
- https://git.kernel.org/stable/c/112fd2f02b308564724b8e81006c254d20945c4b
- https://git.kernel.org/stable/c/611ff1b1ae989a7bcce3e2a8e132ee30e968c557
- https://git.kernel.org/stable/c/e997b357b13a7d95de31681fc54fcc34235fa527
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46762.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46762
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
