# [C] KVM: arm64: vgic: Check the interrupt is still ours before migrating it

## Summary
Severity: Critical
Advisory: CVE-2026-72289
Ecosystem: Linux
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72289
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.7.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: vgic: Check the interrupt is still ours before migrating it

vgic_prune_ap_list() drops both ap_list_lock and irq_lock while migrating
an interrupt to another vCPU. After reacquiring the locks it only checks
that the affinity is unchanged (target_vcpu == vgic_target_oracle(irq))
before moving the interrupt, which assumes that an interrupt whose affinity
is preserved is still queued on this vCPU's ap_list.

That assumption no longer holds if the interrupt is taken off the ap_list
while the locks are dropped. vgic_flush_pending_lpis() removes the
interrupt from the list and sets irq->vcpu to NULL, but leaves
enabled/pending/target_vcpu untouched. As the interrupt is still enabled
and pending, vgic_target_oracle() returns the same target_vcpu, so the
affinity check passes and list_del() is run a second time on an entry that
has already been removed.

Also check that the interrupt is still assigned to this vCPU
(irq->vcpu == vcpu) before moving it.

## References
- https://git.kernel.org/stable/c/0074b82cdfcb5fd13710a0ac308ade68ac6f6fbe
- https://git.kernel.org/stable/c/0658b09cba7fe866c6cd70cd2dcdfdcabe80328f
- https://git.kernel.org/stable/c/3893e1fcf6f306b327a8358dcd1cbd077989a240
- https://git.kernel.org/stable/c/654be81c4c637af12709d47c7efc3302cd336513
- https://git.kernel.org/stable/c/79fdd2aa774e44847cd9bb7edc811e73e3dc7bfe
- https://git.kernel.org/stable/c/cb3efe1a354f1638726725c3ecee1ce8d1a7e2dc
- https://git.kernel.org/stable/c/da2d249a39a1881681c303ceea33f38ba1c5bbeb
- https://git.kernel.org/stable/c/e363c0bc0226dc5ea5046a88e9a6864b82c45399
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72289.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72289
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
