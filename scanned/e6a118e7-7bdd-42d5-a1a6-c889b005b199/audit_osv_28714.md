# [C] net/mlx5: Properly link new fs rules into the tree

## Summary
Severity: Critical
Advisory: CVE-2024-35960
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35960
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.10.216, >=5.11.0 <5.15.156, >=5.16.0 <6.1.87, >=6.2.0 <6.6.28, >=6.7.0 <6.8.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: Properly link new fs rules into the tree

Previously, add_rule_fg would only add newly created rules from the
handle into the tree when they had a refcount of 1. On the other hand,
create_flow_handle tries hard to find and reference already existing
identical rules instead of creating new ones.

These two behaviors can result in a situation where create_flow_handle
1) creates a new rule and references it, then
2) in a subsequent step during the same handle creation references it
   again,
resulting in a rule with a refcount of 2 that is not linked into the
tree, will have a NULL parent and root and will result in a crash when
the flow group is deleted because del_sw_hw_rule, invoked on rule
deletion, assumes node->parent is != NULL.

This happened in the wild, due to another bug related to incorrect
handling of duplicate pkt_reformat ids, which lead to the code in
create_flow_handle incorrectly referencing a just-added rule in the same
flow handle, resulting in the problem described above. Full details are
at [1].

This patch changes add_rule_fg to add new rules without parents into
the tree, properly initializing them and avoiding the crash. This makes
it more consistent with how rules are added to an FTE in
create_flow_handle.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/1263b0b26077b1183c3c45a0a2479573a351d423
- https://git.kernel.org/stable/c/2e8dc5cffc844dacfa79f056dea88002312f253f
- https://git.kernel.org/stable/c/3d90ca9145f6b97b38d0c2b6b30f6ca6af9c1801
- https://git.kernel.org/stable/c/5cf5337ef701830f173b4eec00a4f984adeb57a0
- https://git.kernel.org/stable/c/7aaee12b804c5e0374e7b132b6ec2158ff33dd64
- https://git.kernel.org/stable/c/7c6782ad4911cbee874e85630226ed389ff2e453
- https://git.kernel.org/stable/c/adf67a03af39095f05d82050f15813d6f700159d
- https://git.kernel.org/stable/c/de0139719cdda82806a47580ca0df06fc85e0bd2
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35960.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35960
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
