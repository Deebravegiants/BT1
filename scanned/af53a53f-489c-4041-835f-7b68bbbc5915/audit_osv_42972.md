# [C] netfilter: flowtable: support IPIP tunnel with direct xmit

## Summary
Severity: Critical
Advisory: CVE-2026-72248
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72248
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: flowtable: support IPIP tunnel with direct xmit

The combination of IPIP tunnel with direct xmit, eg. bridge device,
breaks because no dst_entry is provided to check the skb headroom and to
set the iph->frag_off field. This leads to invalid dst usage and can
trigger a crash in the tunnel transmit path.

Fix this by moving dst_cache and dst_cookie out of the runtime union so
that they can be shared by neighbour, xfrm, and direct tunnel flows.
For FLOW_OFFLOAD_XMIT_DIRECT tuples carrying tunnel metadata, preserve
route state in these shared fields and release it through the common
dst release path.

Since dst_entry is now available to the three supported xmit modes and
dst_release() already deals with NULL dst, remove the xmit type check
in nft_flow_dst_release(). Moreover, skip the check if the dst entry
is NULL in nf_flow_dst_check() which is now the case for the direct
xmit case.

Based on patch from Rein Wei <n05ec@lzu.edu.cn>.

## References
- https://git.kernel.org/stable/c/0880c4ed122d0cddc9f29a2b28f055d1f24f0fca
- https://git.kernel.org/stable/c/fa7395c02d95e51bad2952325d2d6503bfbad437
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72248.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72248
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
