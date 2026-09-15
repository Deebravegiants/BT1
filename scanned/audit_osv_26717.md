# [H] tcp: fix skb_copy_ubufs() vs BIG TCP

## Summary
Severity: High
Advisory: CVE-2023-53669
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-07
Source: https://osv.dev/vulnerability/CVE-2023-53669
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.29, >=6.2.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: fix skb_copy_ubufs() vs BIG TCP

David Ahern reported crashes in skb_copy_ubufs() caused by TCP tx zerocopy
using hugepages, and skb length bigger than ~68 KB.

skb_copy_ubufs() assumed it could copy all payload using up to
MAX_SKB_FRAGS order-0 pages.

This assumption broke when BIG TCP was able to put up to 512 KB per skb.

We did not hit this bug at Google because we use CONFIG_MAX_SKB_FRAGS=45
and limit gso_max_size to 180000.

A solution is to use higher order pages if needed.

v2: add missing __GFP_COMP, or we leak memory.

## References
- https://git.kernel.org/stable/c/3c77a377877acbaf03cd7caa21d3644a5dd16301
- https://git.kernel.org/stable/c/7e692df3933628d974acb9f5b334d2b3e885e2a6
- https://git.kernel.org/stable/c/7fa93e39fbb0566019c388a8038a4d58552e0910
- https://git.kernel.org/stable/c/9cd62f0ba465cf647c7d8c2ca7b0d99ea0c1328f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53669.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53669
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
