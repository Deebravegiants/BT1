# [H] KVM: arm64: Bound used_lrs when flushing the pKVM hyp vCPU

## Summary
Severity: High
Advisory: CVE-2026-64287
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64287
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Bound used_lrs when flushing the pKVM hyp vCPU

flush_hyp_vcpu() copies the host vGIC state into the hyp's private vCPU
on every run. The vGIC list register save and restore use used_lrs as
their loop bound and expect it to stay within the number of implemented
list registers. While this is generally the case, flush_hyp_vcpu()
copies vgic_v3 verbatim and does not enforce this, so a value provided
by the host is used at EL2 to index vgic_lr[] and access ICH_LR<n>_EL2
(host -> EL2).

Fix by clamping used_lrs to the number of implemented list registers
after the copy, as the trusted path already does in
vgic_flush_lr_state(). The number of implemented list registers is
constant after init, so it is replicated once from
kvm_vgic_global_state.nr_lr into hyp_gicv3_nr_lr rather than read on
every entry.

## References
- https://git.kernel.org/stable/c/2c5e72b9fbf83fdfa724e9f1af0f418ccf8739b8
- https://git.kernel.org/stable/c/7fca3fcef81c713bc82a37bf741e0f28e6d04a6f
- https://git.kernel.org/stable/c/8cc8bbbfab14c22c5551d0dd19b208a44b141c76
- https://git.kernel.org/stable/c/9fa301d8298778dd799fa4dcf7a7f440715d146e
- https://git.kernel.org/stable/c/c646431865f4b1a5b14067233fa27b11e05e0d46
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64287.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64287
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
