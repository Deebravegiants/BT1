# [H] 9p: trans_fd/p9_conn_cancel: drop client lock earlier

## Summary
Severity: High
Advisory: CVE-2022-49768
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49768
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.334, >=4.10.0 <4.14.300, >=4.15.0 <4.19.267, >=4.19.0 <5.4.225, >=4.20.0 <5.10.156, >=5.5.0 <5.15.80, >=5.11.0 <6.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

9p: trans_fd/p9_conn_cancel: drop client lock earlier

syzbot reported a double-lock here and we no longer need this
lock after requests have been moved off to local list:
just drop the lock earlier.

## References
- https://git.kernel.org/stable/c/52f1c45dde9136f964d63a77d19826c8a74e2c7f
- https://git.kernel.org/stable/c/612c977f5d481f551d03d83d0aef588845c1300c
- https://git.kernel.org/stable/c/82825dbf393f7c7979d462f9609a15bde8092b3f
- https://git.kernel.org/stable/c/96760723aae1b45f733f702abb4333137143909f
- https://git.kernel.org/stable/c/a4f1a01b2e81378fce9ca528d4d8a049e4b58fcd
- https://git.kernel.org/stable/c/e3031280fe4eaf61a09e60823331f81f321be8e1
- https://git.kernel.org/stable/c/f14858bc77c567e089965962877ee726ffad0556
- https://git.kernel.org/stable/c/fec1406f5e7ab20b71f6d231792b0040e3300aaf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49768.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49768
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
