# [H] KVM: TDX: Reject concurrent change to CPUID entry count

## Summary
Severity: High
Advisory: CVE-2026-72285
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72285
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: TDX: Reject concurrent change to CPUID entry count

Reject KVM_TDX_INIT_VM if userspace changes cpuid.nent between the
initial read and the subsequent copy of the initialization data.

tdx_td_init() first reads user_data->cpuid.nent to size the flexible
kvm_tdx_init_vm copy.  The copied structure also contains cpuid.nent,
and that field can differ from the value used to size the allocation if
userspace modifies the input concurrently.  setup_tdparams_cpuids() later
passes init_vm->cpuid.nent to kvm_find_cpuid_entry2(), which uses it as
the array bound for the copied entries.

Require the copied count to match the value used to size the allocation
so that CPUID parsing cannot access beyond the entries actually copied.

## References
- https://git.kernel.org/stable/c/cfbebb55e5127dc162e73fa8956000055a78606c
- https://git.kernel.org/stable/c/d6b5aba65e99531c97b146622a406c75653819d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72285.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72285
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
