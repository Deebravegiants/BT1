# [H] net: mana: Fix Rx DMA datasize and skb_over_panic

## Summary
Severity: High
Advisory: CVE-2024-35901
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35901
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mana: Fix Rx DMA datasize and skb_over_panic

mana_get_rxbuf_cfg() aligns the RX buffer's DMA datasize to be
multiple of 64. So a packet slightly bigger than mtu+14, say 1536,
can be received and cause skb_over_panic.

Sample dmesg:
[ 5325.237162] skbuff: skb_over_panic: text:ffffffffc043277a len:1536 put:1536 head:ff1100018b517000 data:ff1100018b517100 tail:0x700 end:0x6ea dev:<NULL>
[ 5325.243689] ------------[ cut here ]------------
[ 5325.245748] kernel BUG at net/core/skbuff.c:192!
[ 5325.247838] invalid opcode: 0000 [#1] PREEMPT SMP NOPTI
[ 5325.258374] RIP: 0010:skb_panic+0x4f/0x60
[ 5325.302941] Call Trace:
[ 5325.304389]  <IRQ>
[ 5325.315794]  ? skb_panic+0x4f/0x60
[ 5325.317457]  ? asm_exc_invalid_op+0x1f/0x30
[ 5325.319490]  ? skb_panic+0x4f/0x60
[ 5325.321161]  skb_put+0x4e/0x50
[ 5325.322670]  mana_poll+0x6fa/0xb50 [mana]
[ 5325.324578]  __napi_poll+0x33/0x1e0
[ 5325.326328]  net_rx_action+0x12e/0x280

As discussed internally, this alignment is not necessary. To fix
this bug, remove it from the code. So oversized packets will be
marked as CQE_RX_TRUNCATED by NIC, and dropped.

## References
- https://git.kernel.org/stable/c/05cb7c41fa1a7a7b2c2a6b81bbe7c67f5c11932b
- https://git.kernel.org/stable/c/c0de6ab920aafb56feab56058e46b688e694a246
- https://git.kernel.org/stable/c/ca58927b00385005f488b6a9905ced7a4f719aad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35901.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35901
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
