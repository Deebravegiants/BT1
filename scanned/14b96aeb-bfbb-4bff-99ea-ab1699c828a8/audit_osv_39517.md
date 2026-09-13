# [H] ipv4: icmp: validate reply type before using icmp_pointers

## Summary
Severity: High
Advisory: CVE-2026-46037
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-46037
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.86, >=6.13.0 <6.18.27, >=6.19.0 <7.0.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: icmp: validate reply type before using icmp_pointers

Extended echo replies use ICMP_EXT_ECHOREPLY as the outbound reply type.
That value is outside the range covered by icmp_pointers[], which only
describes the traditional ICMP types up to NR_ICMP_TYPES.

Avoid consulting icmp_pointers[] for reply types outside that range, and
use array_index_nospec() for the remaining in-range lookup. Normal ICMP
replies keep their existing behavior unchanged.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/67bf002a2d7387a6312138210d0bd06e3cf4879b
- https://git.kernel.org/stable/c/92e7c209036dcc0e8ffdf806fdfd3645b263bea5
- https://git.kernel.org/stable/c/93df2af4f491de33827550b9d420f01808c0706b
- https://git.kernel.org/stable/c/b3a88fc5ae024d43c5ecf653f3bbe837e4a6dc99
- https://git.kernel.org/stable/c/bc64a66e0b9ad937d3d49934242ee62b01ba9a94
- https://git.kernel.org/stable/c/c2178ff1c70ebfc2ab9651b230c58a34683db759
- https://git.kernel.org/stable/c/d700c34a5d186b9ba0715bcb19e0ff80ffbfbfc1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46037.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46037
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
