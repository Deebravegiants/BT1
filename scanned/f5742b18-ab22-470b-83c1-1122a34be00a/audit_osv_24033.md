# [M] cxl/pmem: Fix cxl_pmem_region and cxl_memdev leak

## Summary
Severity: Medium
Advisory: CVE-2022-49896
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49896
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

cxl/pmem: Fix cxl_pmem_region and cxl_memdev leak

When a cxl_nvdimm object goes through a ->remove() event (device
physically removed, nvdimm-bridge disabled, or nvdimm device disabled),
then any associated regions must also be disabled. As highlighted by the
cxl-create-region.sh test [1], a single device may host multiple
regions, but the driver was only tracking one region at a time. This
leads to a situation where only the last enabled region per nvdimm
device is cleaned up properly. Other regions are leaked, and this also
causes cxl_memdev reference leaks.

Fix the tracking by allowing cxl_nvdimm objects to track multiple region
associations.

## References
- https://git.kernel.org/stable/c/4d07ae22e79ebc2d7528bbc69daa53b86981cb3a
- https://git.kernel.org/stable/c/f43b6bfdbab78606735ba81185cf0602b81e40b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49896.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49896
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
