# [H] tipc: re-fetch skb cb after tipc_msg_validate

## Summary
Severity: High
Advisory: CVE-2022-49017
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2022-49017
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.158, >=5.11.0 <5.15.82, >=5.16.0 <6.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: re-fetch skb cb after tipc_msg_validate

As the call trace shows, the original skb was freed in tipc_msg_validate(),
and dereferencing the old skb cb would cause an use-after-free crash.

  BUG: KASAN: use-after-free in tipc_crypto_rcv_complete+0x1835/0x2240 [tipc]
  Call Trace:
   <IRQ>
   tipc_crypto_rcv_complete+0x1835/0x2240 [tipc]
   tipc_crypto_rcv+0xd32/0x1ec0 [tipc]
   tipc_rcv+0x744/0x1150 [tipc]
  ...
  Allocated by task 47078:
   kmem_cache_alloc_node+0x158/0x4d0
   __alloc_skb+0x1c1/0x270
   tipc_buf_acquire+0x1e/0xe0 [tipc]
   tipc_msg_create+0x33/0x1c0 [tipc]
   tipc_link_build_proto_msg+0x38a/0x2100 [tipc]
   tipc_link_timeout+0x8b8/0xef0 [tipc]
   tipc_node_timeout+0x2a1/0x960 [tipc]
   call_timer_fn+0x2d/0x1c0
  ...
  Freed by task 47078:
   tipc_msg_validate+0x7b/0x440 [tipc]
   tipc_crypto_rcv_complete+0x4b5/0x2240 [tipc]
   tipc_crypto_rcv+0xd32/0x1ec0 [tipc]
   tipc_rcv+0x744/0x1150 [tipc]

This patch fixes it by re-fetching the skb cb from the new allocated skb
after calling tipc_msg_validate().

## References
- https://git.kernel.org/stable/c/1daec0815655e110c6f206c5e777a4af8168ff58
- https://git.kernel.org/stable/c/3067bc61fcfe3081bf4807ce65560f499e895e77
- https://git.kernel.org/stable/c/a1ba595e35aa3afbe417ff0af353afb9f65559c0
- https://git.kernel.org/stable/c/e128190adb2edfd5042105b5d1ed4553f295f5ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49017.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49017
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
