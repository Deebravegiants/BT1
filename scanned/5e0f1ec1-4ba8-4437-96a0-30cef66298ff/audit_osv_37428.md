# [H] LoongArch: KVM: Handle the case that EIOINTC's coremap is empty

## Summary
Severity: High
Advisory: CVE-2026-31569
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31569
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: KVM: Handle the case that EIOINTC's coremap is empty

EIOINTC's coremap in eiointc_update_sw_coremap() can be empty, currently
we get a cpuid with -1 in this case, but we actually need 0 because it's
similar as the case that cpuid >= 4.

This fix an out-of-bounds access to kvm_arch::phyid_map::phys_map[].

## References
- https://git.kernel.org/stable/c/126053d0a685bf1f2e98db8966386f38b2336338
- https://git.kernel.org/stable/c/2a0cbcd28ecf6e0b88fa498bebb94bd1be61a7c3
- https://git.kernel.org/stable/c/b97bd69eb0f67b5f961b304d28e9ba45e202d841
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31569.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31569
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
