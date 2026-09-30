# [H] wifi: mt76: use kfree_rcu for offchannel link in mt76_put_vif_phy_link

## Summary
Severity: High
Advisory: CVE-2026-74325
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74325
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mt76: use kfree_rcu for offchannel link in mt76_put_vif_phy_link

mt76_put_vif_phy_link() frees the offchannel mlink with plain kfree()
after rcu_assign_pointer(NULL). However, rcu_assign_pointer only prevents
future RCU readers from obtaining the pointer -- it does not wait for
existing readers that already hold it via rcu_dereference.

The TX datapath (e.g. mt7996_mac_write_txwi) dereferences mlink->wcid
and mlink->idx under rcu_read_lock. If a TX softirq obtained the pointer
via rcu_dereference just before the NULL assignment, it will dereference
freed memory after the kfree.

struct mt76_vif_link already contains an rcu_head field that is unused at
this free site -- a developer oversight, since the adjacent
kfree_rcu_mightsleep call for rx_sc in the same function shows the
pattern was understood.

Replace kfree(mlink) with kfree_rcu(mlink, rcu_head).

## References
- https://git.kernel.org/stable/c/50e700ac0edce72dee5c3a9755865d9423696ac7
- https://git.kernel.org/stable/c/7fae097aa9a56c30febf539d72ef3773165d3aa3
- https://git.kernel.org/stable/c/c7a83899203ed36696a2d35ddd03c0f522874a63
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74325.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74325
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
