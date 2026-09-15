# [C] bridge: br_nd_send: linearize skb before parsing ND options

## Summary
Severity: Critical
Advisory: CVE-2026-31682
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31682
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.134, >=6.7.0 <6.12.81, >=6.13.0 <6.18.22, >=6.19.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

bridge: br_nd_send: linearize skb before parsing ND options

br_nd_send() parses neighbour discovery options from ns->opt[] and
assumes that these options are in the linear part of request.

Its callers only guarantee that the ICMPv6 header and target address
are available, so the option area can still be non-linear. Parsing
ns->opt[] in that case can access data past the linear buffer.

Linearize request before option parsing and derive ns from the linear
network header.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/2ba4caba423ed94d63006eb1d2227b0332ab7fcd
- https://git.kernel.org/stable/c/3a30f6469b058574f49efde61cd6f5d79e576053
- https://git.kernel.org/stable/c/4f397b950c916e9a1f8a4fce04ea0110206cad47
- https://git.kernel.org/stable/c/658261898130da620fc3d0fbb0523efb3366cb55
- https://git.kernel.org/stable/c/9c55e41c73af5c4511070933b1bd25248521270c
- https://git.kernel.org/stable/c/a01aee7cafc575bb82f5529e8734e7052f9b16ea
- https://git.kernel.org/stable/c/bd91ec85aa4c77d645bd2739fc56784157a88ca2
- https://git.kernel.org/stable/c/c68433fd291c9e88c00292095172c62d1997d662
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31682.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31682
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
