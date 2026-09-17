# [M] l2tp: close all race conditions in l2tp_tunnel_register()

## Summary
Severity: Medium
Advisory: CVE-2023-53020
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53020
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

l2tp: close all race conditions in l2tp_tunnel_register()

The code in l2tp_tunnel_register() is racy in several ways:

1. It modifies the tunnel socket _after_ publishing it.

2. It calls setup_udp_tunnel_sock() on an existing socket without
   locking.

3. It changes sock lock class on fly, which triggers many syzbot
   reports.

This patch amends all of them by moving socket initialization code
before publishing and under sock lock. As suggested by Jakub, the
l2tp lockdep class is not necessary as we can just switch to
bh_lock_sock_nested().

## References
- https://git.kernel.org/stable/c/0b2c59720e65885a394a017d0cf9cab118914682
- https://git.kernel.org/stable/c/2d77e5c0ad79004b5ef901895437e9cce6dfcc7e
- https://git.kernel.org/stable/c/77e8ed776cdb1a24b2aab8fe7c6f1f154235e1ce
- https://git.kernel.org/stable/c/cef0845b6dcfa2f6c2c832e7f9622551456c741d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53020.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53020
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
