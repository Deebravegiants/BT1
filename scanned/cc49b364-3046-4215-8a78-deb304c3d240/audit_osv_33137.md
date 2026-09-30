# [H] drm/hisilicon/hibmc: fix irq_request()'s irq name variable is local

## Summary
Severity: High
Advisory: CVE-2025-39785
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-11
Source: https://osv.dev/vulnerability/CVE-2025-39785
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/hisilicon/hibmc: fix irq_request()'s irq name variable is local

The local variable is passed in request_irq (), and there will be use
after free problem, which will make request_irq failed. Using the global
irq name instead of it to fix.

## References
- https://git.kernel.org/stable/c/06d261a085a11600f5b577bb56a65fb2c3e57d0a
- https://git.kernel.org/stable/c/8bed4ec42a4e0dc8113172696ff076d1eb6d8bcb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39785.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39785
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
