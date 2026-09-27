# [M] irqchip/gic-v3: Fix error handling in gic_populate_ppi_partitions

## Summary
Severity: Medium
Advisory: CVE-2022-49716
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49716
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/gic-v3: Fix error handling in gic_populate_ppi_partitions

of_get_child_by_name() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
When kcalloc fails, it missing of_node_put() and results in refcount
leak. Fix this by goto out_put_node label.

## References
- https://git.kernel.org/stable/c/0b325d993995a321f6ab4e6c51f0504ec092bf5b
- https://git.kernel.org/stable/c/58e67c81e229351027d28c610638378606e33a08
- https://git.kernel.org/stable/c/7c9dd9d23f26dabcfb14148b9acdfba540418b19
- https://git.kernel.org/stable/c/c83c34c57798fc41faefcf078be78683db2f4beb
- https://git.kernel.org/stable/c/ec8401a429ffee34ccf38cebf3443f8d5ae6cb0d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49716.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49716
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
