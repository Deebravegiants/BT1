# [M] regulator: scmi: Fix refcount leak in scmi_regulator_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49466
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49466
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

regulator: scmi: Fix refcount leak in scmi_regulator_probe

of_find_node_by_name() returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/299a002161c7bfb72e99ba45e5b660aecc344ea0
- https://git.kernel.org/stable/c/4a59c763ef9b68c711dc2fd2ef4a6648da5480ee
- https://git.kernel.org/stable/c/68d6c8476fd4f448e70e0ab31ff972838ac41dae
- https://git.kernel.org/stable/c/9ebbfa73d69909b7c737f599fd4ebd42318fc881
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49466.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49466
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
