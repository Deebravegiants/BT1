# [H] KVM: arm64: Fix ID register initialization for non-protected pKVM guests

## Summary
Severity: High
Advisory: CVE-2026-23425
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23425
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.18.17, >=6.19.0 <6.19.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Fix ID register initialization for non-protected pKVM guests

In protected mode, the hypervisor maintains a separate instance of
the `kvm` structure for each VM. For non-protected VMs, this structure is
initialized from the host's `kvm` state.

Currently, `pkvm_init_features_from_host()` copies the
`KVM_ARCH_FLAG_ID_REGS_INITIALIZED` flag from the host without the
underlying `id_regs` data being initialized. This results in the
hypervisor seeing the flag as set while the ID registers remain zeroed.

Consequently, `kvm_has_feat()` checks at EL2 fail (return 0) for
non-protected VMs. This breaks logic that relies on feature detection,
such as `ctxt_has_tcrx()` for TCR2_EL1 support. As a result, certain
system registers (e.g., TCR2_EL1, PIR_EL1, POR_EL1) are not
saved/restored during the world switch, which could lead to state
corruption.

Fix this by explicitly copying the ID registers from the host `kvm` to
the hypervisor `kvm` for non-protected VMs during initialization, since
we trust the host with its non-protected guests' features. Also ensure
`KVM_ARCH_FLAG_ID_REGS_INITIALIZED` is cleared initially in
`pkvm_init_features_from_host` so that `vm_copy_id_regs` can properly
initialize them and set the flag once done.

## References
- https://git.kernel.org/stable/c/7e7c2cf0024d89443a7af52e09e47b1fe634ab17
- https://git.kernel.org/stable/c/858620655c1fbff05997e162fc7d83a3293d5142
- https://git.kernel.org/stable/c/bce3847f7c51b86332bf2e554c9e80ca3820f16c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23425.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23425
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
