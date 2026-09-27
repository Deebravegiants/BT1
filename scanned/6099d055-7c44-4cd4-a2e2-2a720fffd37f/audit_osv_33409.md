# [H] media: videobuf2: forbid remove_bufs when legacy fileio is active

## Summary
Severity: High
Advisory: CVE-2025-40302
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-08
Source: https://osv.dev/vulnerability/CVE-2025-40302
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: videobuf2: forbid remove_bufs when legacy fileio is active

vb2_ioctl_remove_bufs() call manipulates queue internal buffer list,
potentially overwriting some pointers used by the legacy fileio access
mode. Forbid that ioctl when fileio is active to protect internal queue
state between subsequent read/write calls.

## References
- https://git.kernel.org/stable/c/27afd6e066cfd80ddbe22a4a11b99174ac89cced
- https://git.kernel.org/stable/c/a6a493b985bfffac097a4e1be09f98b27729dca8
- https://git.kernel.org/stable/c/e819b34df0a7030a15c968d619fa8a3ed2455c7a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40302.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40302
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
