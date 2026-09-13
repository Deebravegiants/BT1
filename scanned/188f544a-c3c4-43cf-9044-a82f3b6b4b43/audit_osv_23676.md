# [M] mips: cpc: Fix refcount leak in mips_cpc_default_phys_base

## Summary
Severity: Medium
Advisory: CVE-2022-49324
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49324
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.14.283, >=4.15.0 <4.19.247, >=4.16.0 <5.4.198, >=4.20.0 <5.10.122, >=5.5.0 <5.15.47, >=5.11.0 <5.17.15, >=5.16.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

mips: cpc: Fix refcount leak in mips_cpc_default_phys_base

Add the missing of_node_put() to release the refcount incremented
by of_find_compatible_node().

## References
- https://git.kernel.org/stable/c/1699ec1bfb59304a788901474f6bb003f7831b61
- https://git.kernel.org/stable/c/4107fa700f314592850e2c64608f6ede4c077476
- https://git.kernel.org/stable/c/8f843cdfc202caaa5d67db3395d893e56362e43a
- https://git.kernel.org/stable/c/961ee8a6eeef4632a215d995d837b204f8c7c2d4
- https://git.kernel.org/stable/c/aae6b4bb63c694bc91714412718f15468407fe51
- https://git.kernel.org/stable/c/bed702566dcdb6ebe300bc0c62bf3600cf4d5874
- https://git.kernel.org/stable/c/c667b3872a4c435a3f29d4e15971cd8c378b0043
- https://git.kernel.org/stable/c/cc0aed22d33ced9e266c50bdf1cbe668c5acfdf8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49324.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49324
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
