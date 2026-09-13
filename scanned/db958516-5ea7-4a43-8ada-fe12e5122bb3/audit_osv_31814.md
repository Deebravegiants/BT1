# [H] netfilter: nf_tables: reject mismatching sum of field_len with set key length

## Summary
Severity: High
Advisory: CVE-2025-21826
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2025-21826
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.235, >=5.11.0 <5.15.179, >=5.16.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.8.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: reject mismatching sum of field_len with set key length

The field length description provides the length of each separated key
field in the concatenation, each field gets rounded up to 32-bits to
calculate the pipapo rule width from pipapo_init(). The set key length
provides the total size of the key aligned to 32-bits.

Register-based arithmetics still allows for combining mismatching set
key length and field length description, eg. set key length 10 and field
description [ 5, 4 ] leading to pipapo width of 12.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-503939.html
- https://git.kernel.org/stable/c/1b9335a8000fb70742f7db10af314104b6ace220
- https://git.kernel.org/stable/c/2ac254343d3cf228ae0738b2615fedf85d000752
- https://git.kernel.org/stable/c/49b7182b97bafbd5645414aff054b4a65d05823d
- https://git.kernel.org/stable/c/5083a7ae45003456c253e981b30a43f71230b4a3
- https://git.kernel.org/stable/c/6b467c8feac759f4c5c86d708beca2aa2b29584f
- https://git.kernel.org/stable/c/82e491e085719068179ff6a5466b7387cc4bbf32
- https://git.kernel.org/stable/c/ab50d0eff4a939d20c37721fd9766347efcdb6f6
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21826.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21826
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
