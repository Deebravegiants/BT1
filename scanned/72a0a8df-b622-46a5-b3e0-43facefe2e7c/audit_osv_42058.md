# [H] netfilter: ebtables: zero chainstack array

## Summary
Severity: High
Advisory: CVE-2026-64413
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64413
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ebtables: zero chainstack array

sashiko reports:
 looking at ebtables table
 translation, could a sparse cpu_possible_mask lead to an uninitialized pointer
 free?

 If cpu_possible_mask is sparse (for example, CPU 0 and CPU 2 are possible,
 but CPU 1 is not), the allocation loop skips CPU 1. If vmalloc_node() fails at
 CPU 2, the cleanup loop will blindly decrement and call vfree() on
 newinfo->chainstack[1].

Not a real-world bug, such allocation isn't expected to fail
in the first place.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/29bf41a9b59aff9f6197df58641a00037d567ca8
- https://git.kernel.org/stable/c/2ade612967e2cdfb9290ebcb773f302c82f311fa
- https://git.kernel.org/stable/c/42bef500d07b5769d916e9122a3e3fa3fd2245ef
- https://git.kernel.org/stable/c/5ee856e4208acafaaaf7b84824d39b78c21345d6
- https://git.kernel.org/stable/c/9e6c5169db423e51dcc66a73fd15409c0d38e088
- https://git.kernel.org/stable/c/9f74d28e903fa4fdf82f870d0aeadddc8196e41c
- https://git.kernel.org/stable/c/cbfe53599eebffd188938ab6774cc41794f6f9d5
- https://git.kernel.org/stable/c/fc7f105451044501a50cfd530cfa3b472c54acbc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64413.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64413
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
