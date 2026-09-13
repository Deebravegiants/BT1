# [H] gro: fix ownership transfer

## Summary
Severity: High
Advisory: CVE-2024-35890
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35890
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.154, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

gro: fix ownership transfer

If packets are GROed with fraglist they might be segmented later on and
continue their journey in the stack. In skb_segment_list those skbs can
be reused as-is. This is an issue as their destructor was removed in
skb_gro_receive_list but not the reference to their socket, and then
they can't be orphaned. Fix this by also removing the reference to the
socket.

For example this could be observed,

  kernel BUG at include/linux/skbuff.h:3131!  (skb_orphan)
  RIP: 0010:ip6_rcv_core+0x11bc/0x19a0
  Call Trace:
   ipv6_list_rcv+0x250/0x3f0
   __netif_receive_skb_list_core+0x49d/0x8f0
   netif_receive_skb_list_internal+0x634/0xd40
   napi_complete_done+0x1d2/0x7d0
   gro_cell_poll+0x118/0x1f0

A similar construction is found in skb_gro_receive, apply the same
change there.

## References
- https://git.kernel.org/stable/c/2eeab8c47c3c0276e0746bc382f405c9a236a5ad
- https://git.kernel.org/stable/c/5b3b67f731296027cceb3efad881ae281213f86f
- https://git.kernel.org/stable/c/d225b0ac96dc40d7e8ae2bc227eb2c56e130975f
- https://git.kernel.org/stable/c/ed4cccef64c1d0d5b91e69f7a8a6697c3a865486
- https://git.kernel.org/stable/c/fc126c1d51e9552eacd2d717b9ffe9262a8a4cd6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35890.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35890
- https://security.netapp.com/advisory/ntap-20250509-0008/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
