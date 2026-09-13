# [C] phonet: pep: fix use-after-free in pep_get_sb()

## Summary
Severity: Critical
Advisory: CVE-2026-68144
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68144
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

phonet: pep: fix use-after-free in pep_get_sb()

pep_get_sb() doesn't consider that pskb_may_pull() might have relocated
the skb data, and continue to access the older pointer, causing UAF.

Reproduced under KASAN:

  BUG: KASAN: slab-use-after-free in pep_get_sb+0x234/0x3b0
  Read of size 1 at addr ff11000105510f50 by task repro/157
   pep_get_sb+0x234/0x3b0
   pipe_handler_do_rcv+0x5f7/0xa10
   pep_do_rcv+0x203/0x410
   __sk_receive_skb+0x471/0x4a0
   phonet_rcv+0x5b3/0x6c0
   __netif_receive_skb+0xcc/0x1d0

Refetch the header with skb_header_pointer() after pskb_may_pull(), so
the possibly stale pointer is no longer dereferenced. There are better
ways to solve this, but, this is the less instrusive one.

## References
- https://git.kernel.org/stable/c/0f71f852a96af9685858ce59fda34ecbf85c283d
- https://git.kernel.org/stable/c/17f78c0c0d41d738ee236eb6e841e39395188054
- https://git.kernel.org/stable/c/1d81e19fc57a5ee55b4497d01bc0510d76fb9578
- https://git.kernel.org/stable/c/25e3641beb51333bfbb155af2fd2573a61113af2
- https://git.kernel.org/stable/c/8d931a75a38b9bb584a4071f5ebbd52755fc35ee
- https://git.kernel.org/stable/c/a48a889b60f73edb0399a8b08284a2ab0bd0295f
- https://git.kernel.org/stable/c/c4a52cb4da8d57d060b1d52085d25147a238dac2
- https://git.kernel.org/stable/c/df198743859fefba2f824115f8151dd62d7ad6d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68144.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68144
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
