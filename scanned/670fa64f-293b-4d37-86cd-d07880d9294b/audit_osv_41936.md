# [H] net: hsr: defer node table free until after RCU readers

## Summary
Severity: High
Advisory: CVE-2026-64123
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64123
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.3.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hsr: defer node table free until after RCU readers

HSR node-list and node-status generic-netlink operations run under
rcu_read_lock(). They walk hsr->node_db through hsr_get_next_node() and
hsr_get_node_data(), but RTM_DELLINK teardown removes the same node table
with plain list_del() and frees each node immediately.

That lets a generic-netlink reader hold a struct hsr_node pointer across
hsr_dellink(). In a KASAN build, widening the reader window after
hsr_get_next_node() obtains the node reproduces a slab-use-after-free
when the reader copies node->macaddress_A; the freeing stack is
hsr_del_nodes() from hsr_dellink().

Use list_del_rcu() and defer the free through the existing
hsr_free_node_rcu() callback. This matches the lifetime rule used by the
HSR prune paths, which already delete nodes with list_del_rcu() and
call_rcu().

## References
- https://git.kernel.org/stable/c/0ea70fb46940620848c08d9d399455c9e82fecdb
- https://git.kernel.org/stable/c/6324423a8e6591f41a16c09a8f9a84e554ac147c
- https://git.kernel.org/stable/c/7713f4aafb577ff49fa67f0488d9c7dddc64d6ce
- https://git.kernel.org/stable/c/8be6685cdd1255bcc85f9b59e4bfc313aefc5c1b
- https://git.kernel.org/stable/c/8c3af18bb0d7c921a5219194037509463eb2ffde
- https://git.kernel.org/stable/c/aaec7096f9961eb223b5b149abe9495525c205d9
- https://git.kernel.org/stable/c/c5580114e0492bcd2e0a37613ed4c311e3fa3d4d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64123.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64123
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
