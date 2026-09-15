# [H] net: ethernet: ti: am65-cpsw-nuss: Fix skb size by accounting for skb_shared_info

## Summary
Severity: High
Advisory: CVE-2025-38545
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38545
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.39, >=6.13.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: ti: am65-cpsw-nuss: Fix skb size by accounting for skb_shared_info

While transitioning from netdev_alloc_ip_align() to build_skb(), memory
for the "skb_shared_info" member of an "skb" was not allocated. Fix this
by allocating "PAGE_SIZE" as the skb length, accounting for the packet
length, headroom and tailroom, thereby including the required memory space
for skb_shared_info.

## References
- https://git.kernel.org/stable/c/02c4d6c26f1f662da8885b299c224ca6628ad232
- https://git.kernel.org/stable/c/7d6ca0c8c0caf9a13cae2de763bb1f2a9ea7eabb
- https://git.kernel.org/stable/c/fc2fffa2facac15ce711e95f98f954426e025bc5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38545.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38545
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
