# [H] netfilter: nft_compat: ebtables emulation must reject non-bridge targets

## Summary
Severity: High
Advisory: CVE-2026-72416
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72416
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_compat: ebtables emulation must reject non-bridge targets

xtables targets return netfilter verdicts: NF_ACCEPT, NF_DROP, and so
on.  ebtables targets return incompatible verdicts: EBT_ACCEPT,
EBT_DROP, ...   We cannot allow fallback to NFPROTO_UNSPEC.

ebtables doesn't permit this since
11ff7288beb2 ("netfilter: ebtables: reject non-bridge targets")
but that commit missed the nft_compat layer.

## References
- https://git.kernel.org/stable/c/33e1875d6b5b552a2e5652b40074c604199354ee
- https://git.kernel.org/stable/c/9dbba7e694ec045f21ede2f892fb42b81b4e1692
- https://git.kernel.org/stable/c/b3f7a84540a0d014ec42343ff5909657c1bd1994
- https://git.kernel.org/stable/c/c129b0185e707dce405968e21afccd5728b2ce63
- https://git.kernel.org/stable/c/efc17b9240d821c424bc5191a5c6e9384a06293e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72416.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72416
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
