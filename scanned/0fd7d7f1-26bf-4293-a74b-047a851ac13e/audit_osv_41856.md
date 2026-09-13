# [C] net: hsr: fix potential OOB access in supervision frame handling

## Summary
Severity: Critical
Advisory: CVE-2026-64000
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64000
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: hsr: fix potential OOB access in supervision frame handling

Ensure the entire TLV header is linearized before access by adding
sizeof(struct hsr_sup_tlv) to the pskb_may_pull() calls. Without this,
a truncated frame could cause an out-of-bounds access.

## References
- https://git.kernel.org/stable/c/09a37dca090c55ffb1a33f52d8667f1c2367ef48
- https://git.kernel.org/stable/c/71c986c0ba45b7dc574fae27c83e7b6671556f37
- https://git.kernel.org/stable/c/78607a6854a22a2502f68092202e75a39af4865d
- https://git.kernel.org/stable/c/a4b64f3e9c7b8259f7dd251a0313420ba7c01852
- https://git.kernel.org/stable/c/f229426072fc865654a60978bb7fda790a051ff3
- https://git.kernel.org/stable/c/fbd0662f9c9a66e8cc3df3099cca8ed6d3837cc7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64000.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64000
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
