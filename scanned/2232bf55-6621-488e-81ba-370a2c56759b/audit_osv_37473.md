# [H] netfilter: ip6t_rt: reject oversized addrnr in rt_mt6_check()

## Summary
Severity: High
Advisory: CVE-2026-31674
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31674
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ip6t_rt: reject oversized addrnr in rt_mt6_check()

Reject rt match rules whose addrnr exceeds IP6T_RT_HOPS.

rt_mt6() expects addrnr to stay within the bounds of rtinfo->addrs[].
Validate addrnr during rule installation so malformed rules are rejected
before the match logic can use an out-of-range value.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/13e3e30ed3b5b67cc1db2bd58a5d09b0f07debfa
- https://git.kernel.org/stable/c/29ea965a1353bc8303877422f79c8211e9ba9c55
- https://git.kernel.org/stable/c/9d3f027327c2fa265f7f85ead41294792c3296ed
- https://git.kernel.org/stable/c/a28ebf6f99de270d6338ccdc3b49f3e818f99b7b
- https://git.kernel.org/stable/c/af9b7e2b765966457f4ec23be5bd34a141f89574
- https://git.kernel.org/stable/c/c6a503a9f4debc654e3a6a7ca1f7fce6a9953c59
- https://git.kernel.org/stable/c/d8795fde1f78669a87c87ac29fceab2f104daa8c
- https://git.kernel.org/stable/c/ded71f5684df16fa645cca5bf4fe6b0cd8a46119
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31674.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31674
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
