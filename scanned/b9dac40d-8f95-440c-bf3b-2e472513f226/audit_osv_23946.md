# [M] irqchip/gic-v3: Fix refcount leak in gic_populate_ppi_partitions

## Summary
Severity: Medium
Advisory: CVE-2022-49715
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49715
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <4.19.249, >=4.20.0 <5.4.200, >=5.5.0 <5.10.124, >=5.11.0 <5.15.49, >=5.16.0 <5.18.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

irqchip/gic-v3: Fix refcount leak in gic_populate_ppi_partitions

of_find_node_by_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/506a88a5bf261d76a5214c0338a320f2214c67ac
- https://git.kernel.org/stable/c/8d884c08eeb83142a7173cb46bcff0434ec42cf1
- https://git.kernel.org/stable/c/c136c2924a59a399aa789858cfb320d481964fb7
- https://git.kernel.org/stable/c/cc5984cf270b69d03f9f4b27063e535036c659e9
- https://git.kernel.org/stable/c/e824482e2c5edacc961b7dd30a92fd47606c3036
- https://git.kernel.org/stable/c/fa1ad9d4cc47ca2470cd904ad4519f05d7e43a2b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49715.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49715
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
