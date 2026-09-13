# [H] netfilter: xt_policy: fix strict mode inbound policy matching

## Summary
Severity: High
Advisory: CVE-2026-52920
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-52920
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.17 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.33, >=6.19.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: xt_policy: fix strict mode inbound policy matching

match_policy_in() walks sec_path entries from the last transform to the
first one, but strict policy matching needs to consume info->pol[] in
the same forward order as the rule layout.

Derive the strict-match policy position from the number of transforms
already consumed so that multi-element inbound rules are matched
consistently.

## References
- https://git.kernel.org/stable/c/392cc1d8408b5665215c1e9290bbf0f92339b043
- https://git.kernel.org/stable/c/4b2b4d7d4e203c92db8966b163edfacb1f0e1e29
- https://git.kernel.org/stable/c/82664d0f1ba25e4f9a71994954abae24c60f4067
- https://git.kernel.org/stable/c/938867e870fb5471bb16f442aeac81326e05bf65
- https://git.kernel.org/stable/c/b130a6eefa02bd4d475f2f059da8bcfb3e7d18d9
- https://git.kernel.org/stable/c/eb323f7b82d2e2f638de0cc2a177803eb20e0707
- https://git.kernel.org/stable/c/f98b7f85e04b40e28b08c461ded0cc79f14f5509
- https://git.kernel.org/stable/c/fc1c518bb1f054831ecabb32da9b8e1dff9699c6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52920.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-52920
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
