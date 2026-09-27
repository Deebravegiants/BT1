# [M] dmaengine: tegra: Fix memory leak in terminate_all()

## Summary
Severity: Medium
Advisory: CVE-2023-53014
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53014
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: tegra: Fix memory leak in terminate_all()

Terminate vdesc when terminating an ongoing transfer.
This will ensure that the vdesc is present in the desc_terminated list
The descriptor will be freed later in desc_free_list().

This fixes the memory leaks which can happen when terminating an
ongoing transfer.

## References
- https://git.kernel.org/stable/c/567128076d554e41609c61b7d447089094ff72c5
- https://git.kernel.org/stable/c/a7a7ee6f5a019ad72852c001abbce50d35e992f2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53014.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53014
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
