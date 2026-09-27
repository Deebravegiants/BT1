# [H] bpf: Fix regsafe() for pointers to packet

## Summary
Severity: High
Advisory: CVE-2026-43030
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-43030
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.253, >=5.11.0 <6.1.168, >=5.16.0 <6.6.134, >=6.2.0 <6.12.81, >=6.7.0 <6.18.22, >=6.13.0 <6.19.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Fix regsafe() for pointers to packet

In case rold->reg->range == BEYOND_PKT_END && rcur->reg->range == N
regsafe() may return true which may lead to current state with
valid packet range not being explored. Fix the bug.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/015a74476dc1ab6923d89f1ee009aaf43faa7185
- https://git.kernel.org/stable/c/37db6b9726d0bcf91cbdf9d63b558c50da49f968
- https://git.kernel.org/stable/c/7241da033fdc507b920e092dab1f97b945cb0370
- https://git.kernel.org/stable/c/8aebe18069394f4a79d2d82080a0f806da449996
- https://git.kernel.org/stable/c/a8502a79e832b861e99218cbd2d8f4312d62e225
- https://git.kernel.org/stable/c/b52f6d0ef7b308f9d05bbddb78749852f28e8e40
- https://git.kernel.org/stable/c/b99d82706bd1511bb875e3de7154698fd9215c99
- https://git.kernel.org/stable/c/ca995b1462ec6db1e869100ba1fb7356bd3f22f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43030.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43030
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
