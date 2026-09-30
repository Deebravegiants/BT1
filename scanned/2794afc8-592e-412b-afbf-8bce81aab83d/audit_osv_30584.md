# [M] io_uring: check for overflows in io_pin_pages

## Summary
Severity: Medium
Advisory: CVE-2024-53187
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-53187
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring: check for overflows in io_pin_pages

WARNING: CPU: 0 PID: 5834 at io_uring/memmap.c:144 io_pin_pages+0x149/0x180 io_uring/memmap.c:144
CPU: 0 UID: 0 PID: 5834 Comm: syz-executor825 Not tainted 6.12.0-next-20241118-syzkaller #0
Call Trace:
 <TASK>
 __io_uaddr_map+0xfb/0x2d0 io_uring/memmap.c:183
 io_rings_map io_uring/io_uring.c:2611 [inline]
 io_allocate_scq_urings+0x1c0/0x650 io_uring/io_uring.c:3470
 io_uring_create+0x5b5/0xc00 io_uring/io_uring.c:3692
 io_uring_setup io_uring/io_uring.c:3781 [inline]
 ...
 </TASK>

io_pin_pages()'s uaddr parameter came directly from the user and can be
garbage. Don't just add size to it as it can overflow.

## References
- https://git.kernel.org/stable/c/0c0a4eae26ac78379d0c1db053de168a8febc6c9
- https://git.kernel.org/stable/c/29eac3eca72d4c2a71122050c37cd7d8f73ac4f3
- https://git.kernel.org/stable/c/aaa90844afd499c9142d0199dfda74439314c013
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53187.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53187
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
