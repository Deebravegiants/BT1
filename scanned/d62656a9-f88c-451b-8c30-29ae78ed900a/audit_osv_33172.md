# [H] batman-adv: fix OOB read/write in network-coding decode

## Summary
Severity: High
Advisory: CVE-2025-39839
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-39839
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.4.299, >=5.5.0 <5.10.243, >=5.11.0 <5.15.192, >=5.16.0 <6.1.151, >=6.2.0 <6.6.105, >=6.7.0 <6.12.46, >=6.13.0 <6.16.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: fix OOB read/write in network-coding decode

batadv_nc_skb_decode_packet() trusts coded_len and checks only against
skb->len. XOR starts at sizeof(struct batadv_unicast_packet), reducing
payload headroom, and the source skb length is not verified, allowing an
out-of-bounds read and a small out-of-bounds write.

Validate that coded_len fits within the payload area of both destination
and source sk_buffs before XORing.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://cert-portal.siemens.com/productcert/html/ssa-089022.html
- https://git.kernel.org/stable/c/1e36c6c8dc8023b4bbe9a16e819f9998b9b6a183
- https://git.kernel.org/stable/c/20080709457bc1e920eb002483d7d981d9b2ac1c
- https://git.kernel.org/stable/c/30fc47248f02b8a14a61df469e1da4704be1a19f
- https://git.kernel.org/stable/c/5d334bce9fad58cf328d8fa14ea1fff855819863
- https://git.kernel.org/stable/c/a67c6397fcb7e842d3c595243049940970541c48
- https://git.kernel.org/stable/c/bb37252c9af1cb250f34735ee98f80b46be3cef1
- https://git.kernel.org/stable/c/d77b6ff0ce35a6d0b0b7b9581bc3f76d041d4087
- https://git.kernel.org/stable/c/dce6c2aa70e94c04c523b375dfcc664d7a0a560a
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39839.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39839
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
