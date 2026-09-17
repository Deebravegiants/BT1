# [H] skbuff: Account for tail adjustment during pull operations

## Summary
Severity: High
Advisory: CVE-2022-50365
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50365
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.3.0 <5.10.163, >=5.5.0 <5.15.86, >=5.11.0 <6.0.16, >=5.16.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

skbuff: Account for tail adjustment during pull operations

Extending the tail can have some unexpected side effects if a program uses
a helper like BPF_FUNC_skb_pull_data to read partial content beyond the
head skb headlen when all the skbs in the gso frag_list are linear with no
head_frag -

  kernel BUG at net/core/skbuff.c:4219!
  pc : skb_segment+0xcf4/0xd2c
  lr : skb_segment+0x63c/0xd2c
  Call trace:
   skb_segment+0xcf4/0xd2c
   __udp_gso_segment+0xa4/0x544
   udp4_ufo_fragment+0x184/0x1c0
   inet_gso_segment+0x16c/0x3a4
   skb_mac_gso_segment+0xd4/0x1b0
   __skb_gso_segment+0xcc/0x12c
   udp_rcv_segment+0x54/0x16c
   udp_queue_rcv_skb+0x78/0x144
   udp_unicast_rcv_skb+0x8c/0xa4
   __udp4_lib_rcv+0x490/0x68c
   udp_rcv+0x20/0x30
   ip_protocol_deliver_rcu+0x1b0/0x33c
   ip_local_deliver+0xd8/0x1f0
   ip_rcv+0x98/0x1a4
   deliver_ptype_list_skb+0x98/0x1ec
   __netif_receive_skb_core+0x978/0xc60

Fix this by marking these skbs as GSO_DODGY so segmentation can handle
the tail updates accordingly.

## References
- https://git.kernel.org/stable/c/2d59f0ca153e9573ec4f140988c0ccca0eb4181b
- https://git.kernel.org/stable/c/2d7afdcbc9d32423f177ee12b7c93783aea338fb
- https://git.kernel.org/stable/c/331615d837f4979eb91a336a223a5c7f7886ecd5
- https://git.kernel.org/stable/c/668dc454bcbd1da73605201ff43f988c70848215
- https://git.kernel.org/stable/c/6ac417d71b80e74b002313fcd73f7e9008e8e457
- https://git.kernel.org/stable/c/821be5a5ab09a40ba09cb5ba354f18cf7996fea0
- https://git.kernel.org/stable/c/8fb773eed4909ef5dc1bbeb3629a337d3336df7e
- https://git.kernel.org/stable/c/946dd5dc4fcc4123cdfe3942b20012c4448cf89a
- https://git.kernel.org/stable/c/ff3743d00f41d803e6ab9334962b674f3b7fd0cb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50365.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50365
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
