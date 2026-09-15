# [H] netfilter: xt_u32: reject invalid shift counts

## Summary
Severity: High
Advisory: CVE-2026-72350
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72350
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.23 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: xt_u32: reject invalid shift counts

u32_match_it() executes rule-supplied shift operands on a 32-bit
value. A malformed u32 rule can provide a shift count of 32 or more,
triggering an undefined shift out-of-bounds during packet evaluation.

Validate XT_U32_LEFTSH and XT_U32_RIGHTSH operands in
u32_mt_checkentry() and reject malformed rules before they reach the
packet path.

## References
- https://git.kernel.org/stable/c/00d034fe8230dfc5832fe011ff2d81c1a2cc7a29
- https://git.kernel.org/stable/c/0a8b7a6d763775709c601f584e709ae48bcc000a
- https://git.kernel.org/stable/c/64cdf7d30ac18e43df6c48004435febb965809a8
- https://git.kernel.org/stable/c/728f479dc0447ae7eaef87926ff49142e415a811
- https://git.kernel.org/stable/c/a597a722fb71a534138c20359b655726622b5f17
- https://git.kernel.org/stable/c/b33b44250d57ab0e5a1e2571b5285fb0d0a7f382
- https://git.kernel.org/stable/c/ca7c92d9701249e6daf132087756a88cbf2bb2a3
- https://git.kernel.org/stable/c/cce42014415cecd98aa49b3950e7b02ee7c81268
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72350.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72350
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
