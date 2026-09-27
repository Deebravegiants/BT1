# [M] LoongArch: mm: Add p?d_leaf() definitions

## Summary
Severity: Medium
Advisory: CVE-2023-53361
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53361
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: mm: Add p?d_leaf() definitions

When I do LTP test, LTP test case ksm06 caused panic at
	break_ksm_pmd_entry
	  -> pmd_leaf (Huge page table but False)
	  -> pte_present (panic)

The reason is pmd_leaf() is not defined, So like commit 501b81046701
("mips: mm: add p?d_leaf() definitions") add p?d_leaf() definition for
LoongArch.

## References
- https://git.kernel.org/stable/c/303be4b33562a5b689261ced1616bf16ad49efa7
- https://git.kernel.org/stable/c/593ad636bac41d67bdc44c83c6945015471313fc
- https://git.kernel.org/stable/c/77aaf22a9200b9557793c96debead911b80acc1c
- https://git.kernel.org/stable/c/cc9bf2d62f196ec600f9e6ea3a6ced11f54a2df9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53361.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53361
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
