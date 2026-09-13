# [C] x86/virt/sev: Revert "Drop WBINVD before setting MSR_AMD64_SYSCFG_SNP_EN"

## Summary
Severity: Critical
Advisory: CVE-2026-72239
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72239
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/virt/sev: Revert "Drop WBINVD before setting MSR_AMD64_SYSCFG_SNP_EN"

Revert

  99cf1fb58e68 ("x86/virt/sev: Drop WBINVD before setting MSR_AMD64_SYSCFG_SNP_EN").

Section 8.8 of the SNP spec says:

  Before invoking SNP_INIT_EX with INIT_RMP set to 1, software must ensure
  that no CPUs contain dirty cache lines for the memory containing the RMP.

Cachelines can be moved from cache to cache in a dirty state. The
wbinvd_on_all_cpus() before SNP_INIT_EX flushes the caches for each CPU, but
if the IPIs for WBINVD race with this dirty cacheline movement, it is possible
that they may not get flushed, violating the firmware requirement.

Doing wbinvd_on_all_cpus() before setting SNPEn is safer since the RMP
table is not yet in use.

  [ Heroically bisected by Srikanth. ]
  [ bp: Massage commit message. ]

## References
- https://git.kernel.org/stable/c/4c2509f3b79756679a02bea649c6a7501b58f52c
- https://git.kernel.org/stable/c/e5158ff53fdff9c229bf13aa5f75eb17cdcfcd2d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72239.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72239
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
