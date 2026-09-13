# [C] net: wwan: t7xx: Fix napi rx poll issue

## Summary
Severity: Critical
Advisory: CVE-2025-38123
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-03
Source: https://osv.dev/vulnerability/CVE-2025-38123
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.94, >=6.7.0 <6.12.34, >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: wwan: t7xx: Fix napi rx poll issue

When driver handles the napi rx polling requests, the netdev might
have been released by the dellink logic triggered by the disconnect
operation on user plane. However, in the logic of processing skb in
polling, an invalid netdev is still being used, which causes a panic.

BUG: kernel NULL pointer dereference, address: 00000000000000f1
Oops: 0000 [#1] PREEMPT SMP NOPTI
RIP: 0010:dev_gro_receive+0x3a/0x620
[...]
Call Trace:
 <IRQ>
 ? __die_body+0x68/0xb0
 ? page_fault_oops+0x379/0x3e0
 ? exc_page_fault+0x4f/0xa0
 ? asm_exc_page_fault+0x22/0x30
 ? __pfx_t7xx_ccmni_recv_skb+0x10/0x10 [mtk_t7xx (HASH:1400 7)]
 ? dev_gro_receive+0x3a/0x620
 napi_gro_receive+0xad/0x170
 t7xx_ccmni_recv_skb+0x48/0x70 [mtk_t7xx (HASH:1400 7)]
 t7xx_dpmaif_napi_rx_poll+0x590/0x800 [mtk_t7xx (HASH:1400 7)]
 net_rx_action+0x103/0x470
 irq_exit_rcu+0x13a/0x310
 sysvec_apic_timer_interrupt+0x56/0x90
 </IRQ>

## References
- https://git.kernel.org/stable/c/66542e9430c625f878a5b5dc0fe41e3458d614bf
- https://git.kernel.org/stable/c/905fe0845bb27e4eed2ca27ea06e6c4847f1b2b1
- https://git.kernel.org/stable/c/cc89f457d9133a558d4e8ef26dc20843c2d12073
- https://git.kernel.org/stable/c/e2df04e69c3f10b412f54be036dd0ed3b14756cf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38123.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38123
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
