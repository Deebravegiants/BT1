# [H] netfilter: xt_connmark: reject invalid shift parameters

## Summary
Severity: High
Advisory: CVE-2026-72347
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72347
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: xt_connmark: reject invalid shift parameters

Revision 2 of the CONNMARK target accepts user-controlled shift
parameters and applies them to 32-bit mark values in
connmark_tg_shift().

A shift_bits value of 32 or more triggers an undefined-shift bug when
the rule is evaluated. Invalid shift_dir values are also accepted and
silently fall back to the left-shift path.

Reject invalid revision-2 shift parameters in connmark_tg_check() so
malformed rules fail at installation time, before they can reach the
packet path.

## References
- https://git.kernel.org/stable/c/1b47026fb4b35bac850ad6e8a4ad7fc018e09ebc
- https://git.kernel.org/stable/c/230173cc6105bdfb2696d37e6e56687b003fbe63
- https://git.kernel.org/stable/c/4eef84b09a3836919360c4232b0f16651a155eec
- https://git.kernel.org/stable/c/8ace320ac4416f5e5fbcd065309fb2dfcce787b0
- https://git.kernel.org/stable/c/9657bb11a6376ab0a79f05d433713d6944111e9d
- https://git.kernel.org/stable/c/c3fa852d117b3fda72265e4230e3967db4a74fcf
- https://git.kernel.org/stable/c/d8ce63d928b457fba7ed1e302492dfd32293671c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72347.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72347
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
