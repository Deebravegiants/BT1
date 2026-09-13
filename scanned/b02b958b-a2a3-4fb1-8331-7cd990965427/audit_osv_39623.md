# [H] KVM: arm64: Reassign nested_mmus array behind mmu_lock

## Summary
Severity: High
Advisory: CVE-2026-46317
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46317
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Reassign nested_mmus array behind mmu_lock

kvm->arch.nested_mmus[] is walked under kvm->mmu_lock, including from the
MMU notifier path (kvm_unmap_gfn_range() -> kvm_nested_s2_unmap()), which
can run at any time. kvm_vcpu_init_nested() reallocates the array and frees
the old buffer while holding only kvm->arch.config_lock, so such a walker
can reference the freed array.

Allocate the new array outside of mmu_lock, as the allocation can sleep.
Under the lock, copy the existing entries, fix up the back pointers and
reassign the array. Free the old buffer after dropping the lock, as
kvfree() can sleep as well.

## References
- https://git.kernel.org/stable/c/4424dbcb06d68e34e51c019a5781a7dc00731971
- https://git.kernel.org/stable/c/70543358fa08e0f7cebc3447c3b70fe97ad7aaa8
- https://git.kernel.org/stable/c/918450ad6010df6ecd2efde12a1409e011da22d6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46317.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46317
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
