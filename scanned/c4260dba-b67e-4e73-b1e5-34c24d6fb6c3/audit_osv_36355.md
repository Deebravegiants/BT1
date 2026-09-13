# [H] net/sched: cls_u32: use skb_header_pointer_careful()

## Summary
Severity: High
Advisory: CVE-2026-23204
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23204
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.10.260, >=5.11.0 <5.15.209, >=5.16.0 <6.1.167, >=6.2.0 <6.6.124, >=6.7.0 <6.12.70, >=6.13.0 <6.18.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: cls_u32: use skb_header_pointer_careful()

skb_header_pointer() does not fully validate negative @offset values.

Use skb_header_pointer_careful() instead.

GangMin Kim provided a report and a repro fooling u32_classify():

BUG: KASAN: slab-out-of-bounds in u32_classify+0x1180/0x11b0
net/sched/cls_u32.c:221

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/13336a6239b9d7c6e61483017bb8bdfe3ceb10a5
- https://git.kernel.org/stable/c/29681ed51e737be14d18ecd1c304c57002e4b72c
- https://git.kernel.org/stable/c/66e4b63d61c15de6ca5332d9ca6db59a404d7136
- https://git.kernel.org/stable/c/8a672f177ebe19c93d795fbe967846084fbc7943
- https://git.kernel.org/stable/c/cabd1a976375780dabab888784e356f574bbaed8
- https://git.kernel.org/stable/c/cfa745830e45ecb75c061aa34330ee0cac941cc7
- https://git.kernel.org/stable/c/e41a23e61259f5526af875c3b86b3d42a9bae0e5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23204.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23204
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
