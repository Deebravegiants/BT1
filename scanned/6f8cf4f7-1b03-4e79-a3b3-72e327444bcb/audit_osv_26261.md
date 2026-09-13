# [H] net: atlantic: eliminate double free in error handling logic

## Summary
Severity: High
Advisory: CVE-2023-52664
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52664
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <6.1.77, >=6.2.0 <6.6.16, >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: atlantic: eliminate double free in error handling logic

Driver has a logic leak in ring data allocation/free,
where aq_ring_free could be called multiple times on same ring,
if system is under stress and got memory allocation error.

Ring pointer was used as an indicator of failure, but this is
not correct since only ring data is allocated/deallocated.
Ring itself is an array member.

Changing ring allocation functions to return error code directly.
This simplifies error handling and eliminates aq_ring_free
on higher layer.

## References
- https://git.kernel.org/stable/c/0edb3ae8bfa31cd544b0c195bdec00e036002b5d
- https://git.kernel.org/stable/c/b3cb7a830a24527877b0bc900b9bd74a96aea928
- https://git.kernel.org/stable/c/c11a870a73a3bc4cc7df6dd877a45b181795fcbf
- https://git.kernel.org/stable/c/d1fde4a7e1dcc4d49cce285107a7a43c3030878d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52664.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52664
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
