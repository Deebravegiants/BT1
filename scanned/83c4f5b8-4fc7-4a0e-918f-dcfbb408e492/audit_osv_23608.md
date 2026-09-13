# [M] mips: cdmm: Fix refcount leak in mips_cdmm_phys_base

## Summary
Severity: Medium
Advisory: CVE-2022-49211
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49211
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mips: cdmm: Fix refcount leak in mips_cdmm_phys_base

The of_find_compatible_node() function returns a node pointer with
refcount incremented, We should use of_node_put() on it when done
Add the missing of_node_put() to release the refcount.

## References
- https://git.kernel.org/stable/c/4528668ca331f7ce5999b7746657b46db5b3b785
- https://git.kernel.org/stable/c/4680c2ac9aabda82acd23ebbd1f900fb6a889cd3
- https://git.kernel.org/stable/c/69155dc2e04777aa94207a73a8b10f12b8428a68
- https://git.kernel.org/stable/c/721ab4be20d4448dd04c2cc8ed99cd4f3e45f765
- https://git.kernel.org/stable/c/ef1728e3cb9e43f38ed10cde705a7ba2b4ad2d35
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49211.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49211
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
