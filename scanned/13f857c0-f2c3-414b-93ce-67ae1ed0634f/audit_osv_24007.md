# [M] tipc: fix the msg->req tlv len check in tipc_nl_compat_name_table_dump_header

## Summary
Severity: Medium
Advisory: CVE-2022-49862
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49862
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.334, >=4.10.0 <4.14.300, >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.0.0 <5.10.155, >=5.5.0 <5.15.79, >=5.11.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: fix the msg->req tlv len check in tipc_nl_compat_name_table_dump_header

This is a follow-up for commit 974cb0e3e7c9 ("tipc: fix uninit-value
in tipc_nl_compat_name_table_dump") where it should have type casted
sizeof(..) to int to work when TLV_GET_DATA_LEN() returns a negative
value.

syzbot reported a call trace because of it:

  BUG: KMSAN: uninit-value in ...
   tipc_nl_compat_name_table_dump+0x841/0xea0 net/tipc/netlink_compat.c:934
   __tipc_nl_compat_dumpit+0xab2/0x1320 net/tipc/netlink_compat.c:238
   tipc_nl_compat_dumpit+0x991/0xb50 net/tipc/netlink_compat.c:321
   tipc_nl_compat_recv+0xb6e/0x1640 net/tipc/netlink_compat.c:1324
   genl_family_rcv_msg_doit net/netlink/genetlink.c:731 [inline]
   genl_family_rcv_msg net/netlink/genetlink.c:775 [inline]
   genl_rcv_msg+0x103f/0x1260 net/netlink/genetlink.c:792
   netlink_rcv_skb+0x3a5/0x6c0 net/netlink/af_netlink.c:2501
   genl_rcv+0x3c/0x50 net/netlink/genetlink.c:803
   netlink_unicast_kernel net/netlink/af_netlink.c:1319 [inline]
   netlink_unicast+0xf3b/0x1270 net/netlink/af_netlink.c:1345
   netlink_sendmsg+0x1288/0x1440 net/netlink/af_netlink.c:1921
   sock_sendmsg_nosec net/socket.c:714 [inline]
   sock_sendmsg net/socket.c:734 [inline]

## References
- https://git.kernel.org/stable/c/082707d3df191bf5bb8801d43e4ce3dea39ca173
- https://git.kernel.org/stable/c/1c075b192fe41030457cd4a5f7dea730412bca40
- https://git.kernel.org/stable/c/301caa06091af4d5cf056ac8249cbda4e6029c6a
- https://git.kernel.org/stable/c/36769b9477491a7af6635863bd950309c1e1b96c
- https://git.kernel.org/stable/c/55a253a6753a603e80b95932ca971ba514aa6ce7
- https://git.kernel.org/stable/c/6cee2c60bd168279852ac7dbe54c2b70d1028644
- https://git.kernel.org/stable/c/a0ead1d648df9c456baec832b494513ef405949a
- https://git.kernel.org/stable/c/f31dd158580940938f77514b87337a777520185a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49862.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49862
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
