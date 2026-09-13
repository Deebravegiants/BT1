# [H] net/openvswitch: check Ethernet header length in key_extract()

## Summary
Severity: High
Advisory: CVE-2026-74701
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74701
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/openvswitch: check Ethernet header length in key_extract()

When a packet arrives on an ARPHRD_NONE device (e.g. TUN),
ovs_flow_key_extract() trusts the user-provided skb->protocol field: if
it is ETH_P_TEB, the packet is classified as MAC_PROTO_ETHERNET and
key_extract() is called without ensuring the skb has ETH_HLEN (14) bytes
of linear data. key_extract() unconditionally pulls 2 * ETH_ALEN bytes
for MAC addresses and parse_ethertype() pulls 2 more, either of which
triggers a kernel BUG in __skb_pull() when the linear area is too small.

  kernel BUG at include/linux/skbuff.h:2848!
  RIP: 0010:key_extract+0xa7e/0xd90 net/openvswitch/flow.c:933
  ovs_flow_key_extract+0x419/0xa70
  ovs_vport_receive+0x222/0x390
  netdev_frame_hook+0x3e0/0x630
  tun_get_user+0x2d0c/0x38e0

Fixed by calling check_header() in key_extract() before accessing the
Ethernet header.

## References
- https://git.kernel.org/stable/c/0b60b55652ba772b173dddc63f3851e1d2dd5927
- https://git.kernel.org/stable/c/81f9b09f0ea3ba9ab966dd17e9f32625a14555e9
- https://git.kernel.org/stable/c/831471718f6e19aed1a330b03b53190a90e06466
- https://git.kernel.org/stable/c/9b8cfbb58b85bfa7a78fac47fdc77396cd01f699
- https://git.kernel.org/stable/c/a8139285c8925efe59af28a9169bb2fda91bff15
- https://git.kernel.org/stable/c/cf6f8b29befb92173659bcef6a441d274947bfae
- https://git.kernel.org/stable/c/d8bea341b183190ce6c055ab0e64ab78eb9a7290
- https://git.kernel.org/stable/c/e85278afd4890dd190ba3c7a1b1a712b801c9fe1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74701.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74701
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
