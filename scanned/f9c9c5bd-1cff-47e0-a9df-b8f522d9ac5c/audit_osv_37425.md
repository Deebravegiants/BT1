# [H] LoongArch: KVM: Make kvm_get_vcpu_by_cpuid() more robust

## Summary
Severity: High
Advisory: CVE-2026-31558
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31558
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: KVM: Make kvm_get_vcpu_by_cpuid() more robust

kvm_get_vcpu_by_cpuid() takes a cpuid parameter whose type is int, so
cpuid can be negative. Let kvm_get_vcpu_by_cpuid() return NULL for this
case so as to make it more robust.

This fix an out-of-bounds access to kvm_arch::phyid_map::phys_map[].

## References
- https://git.kernel.org/stable/c/2db06c15d8c7a0ccb6108524e16cd9163753f354
- https://git.kernel.org/stable/c/47857b05bd50db01e211a1b6f513d57901cd3e6b
- https://git.kernel.org/stable/c/596c3f8069c4792f22fce8c4452f44410032d910
- https://git.kernel.org/stable/c/878cf6acb4fd8ab4126cf9d369a5bb0e23123418
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31558.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31558
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
