# [H] ax25: properly unshare skbs in ax25_kiss_rcv()

## Summary
Severity: High
Advisory: CVE-2025-39848
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39848
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.4.299, >=5.5.0 <5.10.243, >=5.11.0 <5.15.192, >=5.16.0 <6.1.151, >=6.2.0 <6.6.105, >=6.7.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ax25: properly unshare skbs in ax25_kiss_rcv()

Bernard Pidoux reported a regression apparently caused by commit
c353e8983e0d ("net: introduce per netns packet chains").

skb->dev becomes NULL and we crash in __netif_receive_skb_core().

Before above commit, different kind of bugs or corruptions could happen
without a major crash.

But the root cause is that ax25_kiss_rcv() can queue/mangle input skb
without checking if this skb is shared or not.

Many thanks to Bernard Pidoux for his help, diagnosis and tests.

We had a similar issue years ago fixed with commit 7aaed57c5c28
("phonet: properly unshare skbs in phonet_rcv()").

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/01a2984cb803f2d487b7074f9718db2bf3531f69
- https://git.kernel.org/stable/c/2bd0f67212908243ce88e35bf69fa77155b47b14
- https://git.kernel.org/stable/c/42b46684e2c78ee052d8c2ee8d9c2089233c9094
- https://git.kernel.org/stable/c/5b079be1b9da49ad88fc304c874d4be7085f7883
- https://git.kernel.org/stable/c/7d449b7a6c8ee434d10a483feed7c5c50108cf56
- https://git.kernel.org/stable/c/8156210d36a43e76372312c87eb5ea3dbb405a85
- https://git.kernel.org/stable/c/89064cf534bea4bb28c83fe6bbb26657b19dd5fe
- https://git.kernel.org/stable/c/b1c71d674a308d2fbc83efcf88bfc4217a86aa17
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39848.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39848
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
