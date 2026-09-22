# [H] x86/CPU/AMD: Prevent improper isolation of shared resources in Zen2's op cache

## Summary
Severity: High
Advisory: CVE-2026-46174
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46174
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.256, >=5.11.0 <5.15.207, >=5.16.0 <6.1.173, >=6.2.0 <6.6.139, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/CPU/AMD: Prevent improper isolation of shared resources in Zen2's op cache

Make sure resources are not improperly shared in the op cache and
cause instruction corruption this way.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/1cd85a19748b2407830376a5cbae5c0f126016e5
- https://git.kernel.org/stable/c/1e23b30a80b14e5764657401ee2cca030525ae8e
- https://git.kernel.org/stable/c/251497955f2314cd39d43191e81c6151dead4c7b
- https://git.kernel.org/stable/c/28f5ed477eef166d678d6966762cbc1de9b4f436
- https://git.kernel.org/stable/c/9109489cc8c34e50d15575a3d1ff82af586bc1aa
- https://git.kernel.org/stable/c/c21b90f77687075115d989e53a8ec5e2bb427ab1
- https://git.kernel.org/stable/c/f5bc3aef7df46eaaf423d7413ab8833f704ae576
- https://git.kernel.org/stable/c/ff6fc65b3bf73acc5ee71919154d830ad5431362
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46174.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46174
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
