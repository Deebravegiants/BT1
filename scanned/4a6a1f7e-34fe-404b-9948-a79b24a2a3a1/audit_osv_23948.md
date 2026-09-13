# [M] irqchip/apple-aic: Fix refcount leak in build_fiq_affinity

## Summary
Severity: Medium
Advisory: CVE-2022-49717
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49717
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/apple-aic: Fix refcount leak in build_fiq_affinity

of_find_node_by_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/2dc14cebe5dc053434b507bb24e6821cb795050f
- https://git.kernel.org/stable/c/b1ac803f47cb1615468f35cf1ccb553c52087301
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49717.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49717
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
