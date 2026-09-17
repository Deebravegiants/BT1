# [C] net/tls: fix slab-out-of-bounds bug in decrypt_internal

## Summary
Severity: Critical
Advisory: CVE-2022-49094
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49094
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.189, >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tls: fix slab-out-of-bounds bug in decrypt_internal

The memory size of tls_ctx->rx.iv for AES128-CCM is 12 setting in
tls_set_sw_offload(). The return value of crypto_aead_ivsize()
for "ccm(aes)" is 16. So memcpy() require 16 bytes from 12 bytes
memory space will trigger slab-out-of-bounds bug as following:

==================================================================
BUG: KASAN: slab-out-of-bounds in decrypt_internal+0x385/0xc40 [tls]
Read of size 16 at addr ffff888114e84e60 by task tls/10911

Call Trace:
 <TASK>
 dump_stack_lvl+0x34/0x44
 print_report.cold+0x5e/0x5db
 ? decrypt_internal+0x385/0xc40 [tls]
 kasan_report+0xab/0x120
 ? decrypt_internal+0x385/0xc40 [tls]
 kasan_check_range+0xf9/0x1e0
 memcpy+0x20/0x60
 decrypt_internal+0x385/0xc40 [tls]
 ? tls_get_rec+0x2e0/0x2e0 [tls]
 ? process_rx_list+0x1a5/0x420 [tls]
 ? tls_setup_from_iter.constprop.0+0x2e0/0x2e0 [tls]
 decrypt_skb_update+0x9d/0x400 [tls]
 tls_sw_recvmsg+0x3c8/0xb50 [tls]

Allocated by task 10911:
 kasan_save_stack+0x1e/0x40
 __kasan_kmalloc+0x81/0xa0
 tls_set_sw_offload+0x2eb/0xa20 [tls]
 tls_setsockopt+0x68c/0x700 [tls]
 __sys_setsockopt+0xfe/0x1b0

Replace the crypto_aead_ivsize() with prot->iv_size + prot->salt_size
when memcpy() iv value in TLS_1_3_VERSION scenario.

## References
- https://git.kernel.org/stable/c/2304660ab6c425df64d95301b601424c6a50f28b
- https://git.kernel.org/stable/c/29be1816cbab9a0dc6243120939fd10a92753756
- https://git.kernel.org/stable/c/2b7d14c105dd8f6412eda5a91e1e6154653731e3
- https://git.kernel.org/stable/c/589154d0f18945f41d138a5b4e49e518d294474b
- https://git.kernel.org/stable/c/6e2f1b033b17dedda51d465861b69e58317d6343
- https://git.kernel.org/stable/c/9381fe8c849cfbe50245ac01fc077554f6eaa0e2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49094.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49094
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
