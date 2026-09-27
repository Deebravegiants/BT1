# [H] netfilter: nf_conntrack_h323: fix OOB read in decode_int() CONS case

## Summary
Severity: High
Advisory: CVE-2026-23456
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23456
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.17 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_h323: fix OOB read in decode_int() CONS case

In decode_int(), the CONS case calls get_bits(bs, 2) to read a length
value, then calls get_uint(bs, len) without checking that len bytes
remain in the buffer. The existing boundary check only validates the
2 bits for get_bits(), not the subsequent 1-4 bytes that get_uint()
reads. This allows a malformed H.323/RAS packet to cause a 1-4 byte
slab-out-of-bounds read.

Add a boundary check for len bytes after get_bits() and before
get_uint().

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1e3a3593162c96e8a8de48b1e14f60c3b57fca8a
- https://git.kernel.org/stable/c/41b417ff73a24b2c68134992cc44c88db27f482d
- https://git.kernel.org/stable/c/52235bf88159a1ef16434ab49e47e99c8a09ab20
- https://git.kernel.org/stable/c/6bce72daeccca9aa1746e92d6c3d4784e71f2ebb
- https://git.kernel.org/stable/c/774a434f8c9c8602a976b2536f65d0172a07f4d2
- https://git.kernel.org/stable/c/a2cd54b9348e485d338b3c132338a4410c99afaf
- https://git.kernel.org/stable/c/c95dc674ebf01ecfb40388b6facfc89b81fed3b7
- https://git.kernel.org/stable/c/fb6c3596823ec5dd09c2123340330d7448f51a59
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23456.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23456
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
