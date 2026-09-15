# [H] accel/amdxdna: Hold mm structure across iommu_sva_unbind_device()

## Summary
Severity: High
Advisory: CVE-2026-45931
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45931
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/amdxdna: Hold mm structure across iommu_sva_unbind_device()

Some tests trigger a crash in iommu_sva_unbind_device() due to
accessing iommu_mm after the associated mm structure has been
freed.

Fix this by taking an explicit reference to the mm structure
after successfully binding the device, and releasing it only
after the device is unbound. This ensures the mm remains valid
for the entire SVA bind/unbind lifetime.

## References
- https://git.kernel.org/stable/c/a9162439ad792afcddc04718408ec1380b7a5f63
- https://git.kernel.org/stable/c/f31ccf6278132a35a652fe5eeac3941e1e912398
- https://git.kernel.org/stable/c/f6b4c1d98a7b8040d4d02e89425b3942016a2c2c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45931.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45931
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
