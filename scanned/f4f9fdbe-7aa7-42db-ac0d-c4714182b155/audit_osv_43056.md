# [C] eth: fbnic: don't cache shinfo across skb realloc

## Summary
Severity: Critical
Advisory: CVE-2026-72393
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72393
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

eth: fbnic: don't cache shinfo across skb realloc

fbnic_tx_lso() calls skb_cow_head() which may reallocate the skb
including the shared info. We can't use the pointer calculated
before the call.

    BUG: KASAN: slab-use-after-free in fbnic_tx_lso.isra.0+0x668/0x8e0
    Read of size 4 at addr ff110000262edd98 by task swapper/5/0
    Call Trace:
     fbnic_tx_lso.isra.0+0x668/0x8e0
     fbnic_xmit_frame+0x622/0xba0
     dev_hard_start_xmit+0xf4/0x620

    Allocated by task 8653:
     __alloc_skb+0x11e/0x5f0
     alloc_skb_with_frags+0xcc/0x6c0
     sock_alloc_send_pskb+0x327/0x3f0
     __ip_append_data+0x188b/0x47a0
     ip_make_skb+0x24a/0x300
     udp_sendmsg+0x14d2/0x21e0

    Freed by task 0:
     kfree+0x123/0x5a0
     pskb_expand_head+0x36c/0xfa0
     fbnic_tx_lso.isra.0+0x500/0x8e0
     fbnic_xmit_frame+0x622/0xba0
     dev_hard_start_xmit+0xf4/0x620
     sch_direct_xmit+0x25b/0x1100

    The buggy address belongs to the object at ff110000262edc40
     which belongs to the cache skbuff_small_head of size 640
    The buggy address is located 344 bytes inside of
     freed 640-byte region [ff110000262edc40, ff110000262ede

## References
- https://git.kernel.org/stable/c/21f304c2aae46625e050c28d979f4b9d83faa85e
- https://git.kernel.org/stable/c/62b68b774f06bf52e329f254f0199bc43d350ccf
- https://git.kernel.org/stable/c/83df3e2594cd78aa40b1246a19879abb4891945b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72393.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72393
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
