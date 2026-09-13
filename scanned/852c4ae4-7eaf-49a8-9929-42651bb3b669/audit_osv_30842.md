# [H] ksmbd: fix Out-of-Bounds Read in ksmbd_vfs_stream_read

## Summary
Severity: High
Advisory: CVE-2024-56627
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56627
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.176, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix Out-of-Bounds Read in ksmbd_vfs_stream_read

An offset from client could be a negative value, It could lead
to an out-of-bounds read from the stream_buf.
Note that this issue is coming when setting
'vfs objects = streams_xattr parameter' in ksmbd.conf.

## References
- https://git.kernel.org/stable/c/27de4295522e9a33e4a3fc72f7b8193df9eebe41
- https://git.kernel.org/stable/c/6bd1bf0e8c42f10a9a9679a4c103a9032d30594d
- https://git.kernel.org/stable/c/81eed631935f2c52cdaf6691c6d48e0b06e8ad73
- https://git.kernel.org/stable/c/de4d790dcf53be41736239d7ee63849a16ff5d10
- https://git.kernel.org/stable/c/fc342cf86e2dc4d2edb0fc2ff5e28b6c7845adb9
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56627.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56627
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
