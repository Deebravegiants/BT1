# [H] macsec: fix replay protection at XPN lower-PN wrap

## Summary
Severity: High
Advisory: CVE-2026-63925
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63925
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

macsec: fix replay protection at XPN lower-PN wrap

In macsec_post_decrypt(), when pn is U32_MAX, pn + 1 overflows u32 to 0
and the first branch never fires. If next_pn_halves.lower is also in the
upper half, pn_same_half(pn, lower) is true and the XPN else-if does not
fire either, leaving next_pn_halves unchanged. An attacker that captures
the legitimate frame carrying pn == 0xFFFFFFFF on an XPN association
can then replay it indefinitely, since lowest_pn never rises above
the captured pn and macsec_decrypt() reconstructs the same IV.

Extend the XPN else-if to also fire when pn + 1 wraps to 0, so receipt
of pn == U32_MAX advances next_pn_halves to (upper + 1, 0).

## References
- https://git.kernel.org/stable/c/23c0e230eab397d7f68be2538790ac41d3bb91fd
- https://git.kernel.org/stable/c/679e13a65e68a67c8b3c0467c02ee89157ec6f0f
- https://git.kernel.org/stable/c/6d00f5c7e5ff7ec4795b7f5f8ed88bd346641652
- https://git.kernel.org/stable/c/79495a1b0944fe31ffd54b54b00211b493590d62
- https://git.kernel.org/stable/c/d15130461df388136b62a7b0ce9f66e7e2fa9ff1
- https://git.kernel.org/stable/c/d55acbe577db892b60547b6ef1c020b359331a6d
- https://git.kernel.org/stable/c/dd7306779c6ce1238f4cdc34f3c1f2246b854457
- https://git.kernel.org/stable/c/e68842b3356471ba56c882209f324613dac47f64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63925.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63925
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
