# [H] s390/pkey: Check length in PKEY_VERIFYPROTK ioctl

## Summary
Severity: High
Advisory: CVE-2026-64559
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-64559
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/pkey: Check length in PKEY_VERIFYPROTK ioctl

Explicitly check the buffer length request structure provided by
user-space and fail, if it exceeds the buffer size.

## References
- https://git.kernel.org/stable/c/0a9e34ccbe772b8f321388cdbdf4f22b94e513e7
- https://git.kernel.org/stable/c/693bf91d4db134f9b1c2840c8e287eee3d993bac
- https://git.kernel.org/stable/c/7e7e03848c918aa0acad5ffd75d929e3afec1554
- https://git.kernel.org/stable/c/b3d4ab2d7df9426f7f1d3671d7e2108f2ca6e970
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64559.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64559
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
