# [M] device property: fix of node refcount leak in fwnode_graph_get_next_endpoint()

## Summary
Severity: Medium
Advisory: CVE-2022-49752
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49752
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

device property: fix of node refcount leak in fwnode_graph_get_next_endpoint()

The 'parent' returned by fwnode_graph_get_port_parent()
with refcount incremented when 'prev' is not NULL, it
needs be put when finish using it.

Because the parent is const, introduce a new variable to
store the returned fwnode, then put it before returning
from fwnode_graph_get_next_endpoint().

## References
- https://git.kernel.org/stable/c/39af728649b05e88a2b40e714feeee6451c3f18e
- https://git.kernel.org/stable/c/7701a4bd45c11f9a289d8f262fad05705a012339
- https://git.kernel.org/stable/c/e0472947bead3af94cc968ce35fc0414803a2f65
- https://git.kernel.org/stable/c/e75485fc589ec729cc182aa9b41dfb6c15ae6f6e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49752.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49752
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
