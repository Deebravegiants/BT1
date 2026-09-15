# [M] pinctrl: intel: platform: fix error path in device_for_each_child_node()

## Summary
Severity: Medium
Advisory: CVE-2024-50197
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50197
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

pinctrl: intel: platform: fix error path in device_for_each_child_node()

The device_for_each_child_node() loop requires calls to
fwnode_handle_put() upon early returns to decrement the refcount of
the child node and avoid leaking memory if that error path is triggered.

There is one early returns within that loop in
intel_platform_pinctrl_prepare_community(), but fwnode_handle_put() is
missing.

Instead of adding the missing call, the scoped version of the loop can
be used to simplify the code and avoid mistakes in the future if new
early returns are added, as the child node is only used for parsing, and
it is never assigned.

## References
- https://git.kernel.org/stable/c/16a6d2e685e8f9a2f51dd5a363d3f97fcad35e22
- https://git.kernel.org/stable/c/be3f7b9f995a6c2ee02767a0319929a2a98adf69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50197.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50197
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
