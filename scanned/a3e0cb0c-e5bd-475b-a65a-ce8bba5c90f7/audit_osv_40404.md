# [H] thunderbolt: Validate XDomain request packet size before type cast

## Summary
Severity: High
Advisory: CVE-2026-53147
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53147
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

thunderbolt: Validate XDomain request packet size before type cast

tb_xdp_handle_request() casts the received packet buffer to
protocol-specific structs without verifying that the allocation
is large enough for the target type.  A peer can send a minimal
XDomain packet that passes the generic header length check but is
shorter than the struct accessed after the cast, causing out-of-
bounds reads from the kmemdup allocation.

Plumb the packet length through xdomain_request_work and validate
it against the expected struct size before each cast.

## References
- https://git.kernel.org/stable/c/07cd2787cdf8942d24a1a3ef81aa89b526fb6381
- https://git.kernel.org/stable/c/0dd61ba03d05187726ecdf9c0e2175a81b9b24f6
- https://git.kernel.org/stable/c/46da5c3ea011e884028a91cf913db093920a915b
- https://git.kernel.org/stable/c/79235c8add5da4bf27a12f5a5dbb579f300c059e
- https://git.kernel.org/stable/c/a504b9f2797b739e0304d537e8aa4ce883ecce39
- https://git.kernel.org/stable/c/a770e62923090d7572f1f5a8507ae551d354a057
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53147.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53147
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
