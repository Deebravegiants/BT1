# [C] ksmbd: fix integer overflows on 32 bit systems

## Summary
Severity: Critical
Advisory: CVE-2025-21748
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21748
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.78, >=6.7.0 <6.12.14, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix integer overflows on 32 bit systems

On 32bit systems the addition operations in ipc_msg_alloc() can
potentially overflow leading to memory corruption.
Add bounds checking using KSMBD_IPC_MAX_PAYLOAD to avoid overflow.

## References
- https://git.kernel.org/stable/c/760568c1f62ea874e8fb492f9cfa4f47b4b8391e
- https://git.kernel.org/stable/c/82f59d64e6297f270311b16b5dcf65be406d1ea3
- https://git.kernel.org/stable/c/aab98e2dbd648510f8f51b83fbf4721206ccae45
- https://git.kernel.org/stable/c/b4b902737746c490258de5cb55cab39e79927a67
- https://git.kernel.org/stable/c/ecb9947fa7c99a77b04d43404c6988a0d326e4a0
- https://git.kernel.org/stable/c/f3b9fb2764591d792d160f375851013665a9e820
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21748.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21748
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
