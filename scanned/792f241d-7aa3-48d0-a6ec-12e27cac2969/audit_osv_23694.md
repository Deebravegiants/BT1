# [M] net: dsa: lantiq_gswip: Fix refcount leak in gswip_gphy_fw_list

## Summary
Severity: Medium
Advisory: CVE-2022-49346
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49346
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dsa: lantiq_gswip: Fix refcount leak in gswip_gphy_fw_list

Every iteration of for_each_available_child_of_node() decrements
the reference count of the previous node.
when breaking early from a for_each_available_child_of_node() loop,
we need to explicitly call of_node_put() on the gphy_fw_np.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/0737e018a05e2aa352828c52bdeed3b02cff2930
- https://git.kernel.org/stable/c/2e007ac6fa7c9c94ad84da075c5c504afad690a0
- https://git.kernel.org/stable/c/32cd78c5610f02a929f63cac985e73692d05f33e
- https://git.kernel.org/stable/c/54d6802c4d83fa8de7696cfec06f475d5fd92d27
- https://git.kernel.org/stable/c/7c8df6fad43d9d5d77f281f794b2a93cd02fd1a9
- https://git.kernel.org/stable/c/c2ae49a113a5344232f1ebb93bcf18bbd11e9c39
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49346.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49346
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
