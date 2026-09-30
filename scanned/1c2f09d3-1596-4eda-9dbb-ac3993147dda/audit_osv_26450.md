# [M] spi: imx: Don't skip cleanup in remove's error path

## Summary
Severity: Medium
Advisory: CVE-2023-53225
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53225
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: imx: Don't skip cleanup in remove's error path

Returning early in a platform driver's remove callback is wrong. In this
case the dma resources are not released in the error path. this is never
retried later and so this is a permanent leak. To fix this, only skip
hardware disabling if waking the device fails.

## References
- https://git.kernel.org/stable/c/11951c9e3f364d7ae3b568a0e52c8335d43066b5
- https://git.kernel.org/stable/c/57a463226638f1ceabbb029cbd21b0c94640f1b5
- https://git.kernel.org/stable/c/6d16305a1535873e0a8a8ae92ea2d9106ec2d7df
- https://git.kernel.org/stable/c/aa93a46f998a9069368026ac52bba96868c59157
- https://git.kernel.org/stable/c/b64cb3f085fed296103c91f0db6acad30a021b36
- https://git.kernel.org/stable/c/f90822ad63d11301e425311dac0c8e12ca1737b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53225.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53225
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
