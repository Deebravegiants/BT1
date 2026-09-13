# [H] x86/mm: Fix SMP ordering in switch_mm_irqs_off()

## Summary
Severity: High
Advisory: CVE-2025-40174
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40174
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.17.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/mm: Fix SMP ordering in switch_mm_irqs_off()

Stephen noted that it is possible to not have an smp_mb() between
the loaded_mm store and the tlb_gen load in switch_mm(), meaning the
ordering against flush_tlb_mm_range() goes out the window, and it
becomes possible for switch_mm() to not observe a recent tlb_gen
update and fail to flush the TLBs.

[ dhansen: merge conflict fixed by Ingo ]

## References
- https://git.kernel.org/stable/c/0fe5e3f5fb75c5d88dad24dece3ee75e9d87adeb
- https://git.kernel.org/stable/c/83b0177a6c4889b3a6e865da5e21b2c9d97d0551
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40174.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40174
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
