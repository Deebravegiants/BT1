# [C] net: atlantic: fix fragment overflow handling in RX path

## Summary
Severity: Critical
Advisory: CVE-2025-68301
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68301
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.247, >=5.11.0 <5.15.197, >=5.16.0 <6.1.159, >=5.18.0 <6.6.119, >=6.2.0 <6.12.61, >=6.7.0 <6.17.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: atlantic: fix fragment overflow handling in RX path

The atlantic driver can receive packets with more than MAX_SKB_FRAGS (17)
fragments when handling large multi-descriptor packets. This causes an
out-of-bounds write in skb_add_rx_frag_netmem() leading to kernel panic.

The issue occurs because the driver doesn't check the total number of
fragments before calling skb_add_rx_frag(). When a packet requires more
than MAX_SKB_FRAGS fragments, the fragment index exceeds the array bounds.

Fix by assuming there will be an extra frag if buff->len > AQ_CFG_RX_HDR_SIZE,
then all fragments are accounted for. And reusing the existing check to
prevent the overflow earlier in the code path.

This crash occurred in production with an Aquantia AQC113 10G NIC.

Stack trace from production environment:
```
RIP: 0010:skb_add_rx_frag_netmem+0x29/0xd0
Code: 90 f3 0f 1e fa 0f 1f 44 00 00 48 89 f8 41 89
ca 48 89 d7 48 63 ce 8b 90 c0 00 00 00 48 c1 e1 04 48 01 ca 48 03 90
c8 00 00 00 <48> 89 7a 30 44 89 52 3c 44 89 42 38 40 f6 c7 01 75 74 48
89 fa 83
RSP: 0018:ffffa9bec02a8d50 EFLAGS: 00010287
RAX: ffff925b22e80a00 RBX: ffff925ad38d2700 RCX:
fffffffe0a0c8000
RDX: ffff9258ea95bac0 RSI: ffff925ae0a0c800 RDI:
0000000000037a40
RBP: 0000000000000024 R08: 0000000000000000 R09:
0000000000000021
R10: 0000000000000848 R11: 0000000000000000 R12:
ffffa9bec02a8e24
R13: ffff925ad8615570 R14: 0000000000000000 R15:
ffff925b22e80a00
FS: 0000000000000000(0000)
GS:ffff925e47880000(0000) knlGS:0000000000000000
CS: 0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: ffff9258ea95baf0 CR3: 0000000166022004 CR4:
0000000000f72ef0
PKRU: 55555554
Call Trace:
<IRQ>
aq_ring_rx_clean+0x175/0xe60 [atlantic]
? aq_ring_rx_clean+0x14d/0xe60 [atlantic]
? aq_ring_tx_clean+0xdf/0x190 [atlantic]
? kmem_cache_free+0x348/0x450
? aq_vec_poll+0x81/0x1d0 [atlantic]
? __napi_poll+0x28/0x1c0
? net_rx_action+0x337/0x420
```

Changes in v4:
- Add Fixes: tag to satisfy patch validation requirements.

Changes in v3:
- Fix by assuming there will be an extra frag if buff->len > AQ_CFG_RX_HDR_SIZE,
  then all fragments are accounted for.

## References
- https://git.kernel.org/stable/c/34147477eeab24077fcfe9649e282849347d760c
- https://git.kernel.org/stable/c/3be37c3c96b16462394fcb8e15e757c691377038
- https://git.kernel.org/stable/c/3fd2105e1b7e041cc24be151c9a31a14d5fc50ab
- https://git.kernel.org/stable/c/5d6051ea1b0417ae2f06a8440d22e48fbc8f8997
- https://git.kernel.org/stable/c/5ffcb7b890f61541201461580bb6622ace405aec
- https://git.kernel.org/stable/c/64e47cd1fd631a21bf5a630cebefec6c8fc381cd
- https://git.kernel.org/stable/c/b0c4d5135b04ea100988e2458c98f2d8564cda16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68301.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68301
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
