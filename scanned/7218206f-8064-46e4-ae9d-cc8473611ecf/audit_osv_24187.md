# [M] mm/mempolicy: fix memory leak in set_mempolicy_home_node system call

## Summary
Severity: Medium
Advisory: CVE-2022-50391
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50391
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <6.0.17, >=6.1.0 <6.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/mempolicy: fix memory leak in set_mempolicy_home_node system call

When encountering any vma in the range with policy other than MPOL_BIND or
MPOL_PREFERRED_MANY, an error is returned without issuing a mpol_put on
the policy just allocated with mpol_dup().

This allows arbitrary users to leak kernel memory.

## References
- https://git.kernel.org/stable/c/0ce4cc6d269ddc448a825955b495f662f5d9e153
- https://git.kernel.org/stable/c/38ce7c9bdfc228c14d7621ba36d3eebedd9d4f76
- https://git.kernel.org/stable/c/4ca0eb6b2f3add8c5daefb726ce57dc95d103d33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50391.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50391
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
