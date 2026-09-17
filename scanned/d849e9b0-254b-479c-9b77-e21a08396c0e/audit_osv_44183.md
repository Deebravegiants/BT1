# [H] s390/vfio_ccw: Free all memory if cp_init() fails

## Summary
Severity: High
Advisory: CVE-2026-80555
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-80555
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/vfio_ccw: Free all memory if cp_init() fails

The routine cp_free() is called to unpin/free any memory once an I/O
is completed successfully, or if cp_prefetch() fails. But if cp_init()
fails, and cp->initialized is not enabled, the same routine cannot be
used to free all the memory.

An attempt to address this exists in ccwchain_handle_ccw(), where a
single call to ccwchain_free() is made for the currently-processed
CCW segment. But this will leak other segments (created as a result
of a Transfer in Channel) that had been allocated as part of the same
channel program.

Address this by performing the cleanup outside of the recursive
ccwchain_handle_ccw()/ccwchain_loop_tic() logic.

## References
- https://git.kernel.org/stable/c/152fcb74a26804b70909381c6acc90595a0ae1c1
- https://git.kernel.org/stable/c/17e01e342af74de12899c206dcc9ec90684703aa
- https://git.kernel.org/stable/c/276bd7ed34d56c48c65c43c0b08f2ee77029b2fa
- https://git.kernel.org/stable/c/32e3d364a7b8295120d37e6a6bd433d2de26f748
- https://git.kernel.org/stable/c/4699b54fada156534cbb39834d47fc9374d7a1f5
- https://git.kernel.org/stable/c/6a917199aaf97904f5619afe3dfdacb155b03e8c
- https://git.kernel.org/stable/c/74186c2968f8f756ac3226b545b598457c910c75
- https://git.kernel.org/stable/c/f9bcff265556796834122f95de16d52a8375206c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80555.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80555
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
