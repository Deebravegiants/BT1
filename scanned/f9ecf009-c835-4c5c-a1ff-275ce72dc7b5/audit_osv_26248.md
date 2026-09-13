# [H] netfilter: nf_tables: disallow timeout for anonymous sets

## Summary
Severity: High
Advisory: CVE-2023-52620
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-21
Source: https://osv.dev/vulnerability/CVE-2023-52620
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.1.0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.151, >=5.16.0 <6.1.81

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: disallow timeout for anonymous sets

Never used from userspace, disallow these parameters.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/00b19ee0dcc1aef06294471ab489bae26d94524e
- https://git.kernel.org/stable/c/116b0e8e4673a5faa8a739a19b467010c4d3058c
- https://git.kernel.org/stable/c/49ce99ae43314d887153e07cec8bb6a647a19268
- https://git.kernel.org/stable/c/6f3ae02bbb62f151b19162d5fdc9fe3d48450323
- https://git.kernel.org/stable/c/b7be6c737a179a76901c872f6b4c1d00552d9a1b
- https://git.kernel.org/stable/c/e26d3009efda338f19016df4175f354a9bd0a4ab
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52620.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52620
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
