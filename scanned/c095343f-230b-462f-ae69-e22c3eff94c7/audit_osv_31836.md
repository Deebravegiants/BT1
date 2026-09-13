# [H] s390/ism: add release function for struct device

## Summary
Severity: High
Advisory: CVE-2025-21856
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-21856
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.80, >=6.7.0 <6.12.17, >=6.13.0 <6.13.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/ism: add release function for struct device

According to device_release() in /drivers/base/core.c,
a device without a release function is a broken device
and must be fixed.

The current code directly frees the device after calling device_add()
without waiting for other kernel parts to release their references.
Thus, a reference could still be held to a struct device,
e.g., by sysfs, leading to potential use-after-free
issues if a proper release function is not set.

## References
- https://git.kernel.org/stable/c/0505ff2936f166405d81d0d454a81d9c14124344
- https://git.kernel.org/stable/c/915e34d5ad35a6a9e56113f852ade4a730fb88f0
- https://git.kernel.org/stable/c/940d15254d2216b585558bcf36312da50074e711
- https://git.kernel.org/stable/c/e26e8ac27351f457091459a0a355bacd06d5bb2b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21856.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21856
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
