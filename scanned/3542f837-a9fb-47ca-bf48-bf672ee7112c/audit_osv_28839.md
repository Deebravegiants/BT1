# [H] fs/proc/task_mmu: fix loss of young/dirty bits during pagemap scan

## Summary
Severity: High
Advisory: CVE-2024-36943
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2024-05-30
Source: https://osv.dev/vulnerability/CVE-2024-36943
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.8.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/proc/task_mmu: fix loss of young/dirty bits during pagemap scan

make_uffd_wp_pte() was previously doing:

  pte = ptep_get(ptep);
  ptep_modify_prot_start(ptep);
  pte = pte_mkuffd_wp(pte);
  ptep_modify_prot_commit(ptep, pte);

But if another thread accessed or dirtied the pte between the first 2
calls, this could lead to loss of that information.  Since
ptep_modify_prot_start() gets and clears atomically, the following is the
correct pattern and prevents any possible race.  Any access after the
first call would see an invalid pte and cause a fault:

  pte = ptep_modify_prot_start(ptep);
  pte = pte_mkuffd_wp(pte);
  ptep_modify_prot_commit(ptep, pte);

## References
- https://git.kernel.org/stable/c/74b3d66f91d9f539f99faad74d796fa9a389a015
- https://git.kernel.org/stable/c/c70dce4982ce1718bf978a35f8e26160b82081f4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36943.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36943
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
