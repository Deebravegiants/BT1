# [M] iommu/vt-d: Avoid use of NULL after WARN_ON_ONCE

## Summary
Severity: Medium
Advisory: CVE-2025-21833
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2025-21833
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.57, >=6.13.0 <6.13.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

iommu/vt-d: Avoid use of NULL after WARN_ON_ONCE

There is a WARN_ON_ONCE to catch an unlikely situation when
domain_remove_dev_pasid can't find the `pasid`. In case it nevertheless
happens we must avoid using a NULL pointer.

## References
- https://git.kernel.org/stable/c/60f030f7418d3f1d94f2fb207fe3080e1844630b
- https://git.kernel.org/stable/c/68ec78beb4a3fb0877cbaaf49758c85410c05977
- https://git.kernel.org/stable/c/df96876be3b064aefc493f760e0639765d13ed0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21833.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21833
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
