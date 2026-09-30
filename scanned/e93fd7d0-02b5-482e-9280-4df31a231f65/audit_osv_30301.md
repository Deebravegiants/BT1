# [M] net: enetc: allocate vf_state during PF probes

## Summary
Severity: Medium
Advisory: CVE-2024-50298
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50298
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <6.1.167, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: enetc: allocate vf_state during PF probes

In the previous implementation, vf_state is allocated memory only when VF
is enabled. However, net_device_ops::ndo_set_vf_mac() may be called before
VF is enabled to configure the MAC address of VF. If this is the case,
enetc_pf_set_vf_mac() will access vf_state, resulting in access to a null
pointer. The simplified error log is as follows.

root@ls1028ardb:~# ip link set eno0 vf 1 mac 00:0c:e7:66:77:89
[  173.543315] Unable to handle kernel NULL pointer dereference at virtual address 0000000000000004
[  173.637254] pc : enetc_pf_set_vf_mac+0x3c/0x80 Message from sy
[  173.641973] lr : do_setlink+0x4a8/0xec8
[  173.732292] Call trace:
[  173.734740]  enetc_pf_set_vf_mac+0x3c/0x80
[  173.738847]  __rtnl_newlink+0x530/0x89c
[  173.742692]  rtnl_newlink+0x50/0x7c
[  173.746189]  rtnetlink_rcv_msg+0x128/0x390
[  173.750298]  netlink_rcv_skb+0x60/0x130
[  173.754145]  rtnetlink_rcv+0x18/0x24
[  173.757731]  netlink_unicast+0x318/0x380
[  173.761665]  netlink_sendmsg+0x17c/0x3c8

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/35668e29e979b3a1927d3959cdd87327afd8e5eb
- https://git.kernel.org/stable/c/7eb923f8d4819737c07d6a8d0daef0a4d7f99e0c
- https://git.kernel.org/stable/c/e15c5506dd39885cd047f811a64240e2e8ab401b
- https://git.kernel.org/stable/c/ef0edfbe9eeed1fccad7cb705648af5222664944
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50298.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50298
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
