# [H] KVM: arm64: nv: Fix SPSR_EL2 restore in kvm_hyp_handle_mops()

## Summary
Severity: High
Advisory: CVE-2026-64555
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64555
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: nv: Fix SPSR_EL2 restore in kvm_hyp_handle_mops()

kvm_hyp_handle_mops() resets the single-step state machine as part of
rewinding state for a MOPS exception by modifying vcpu_cpsr() and
writing the result directly into hardware.

In the case of nested virtualization, vcpu_cpsr() is a synthetic value
such that the rest of KVM can deal with vEL2 cleanly. That means the
value requires translation before being written into hardware, which is
unfortunately missing from the MOPS handler.

Fix it by directly modifying SPSR_EL2 and avoiding the synthetic state
altogether, which will be resynchronized on the next 'full' exit back
to KVM.

## References
- https://git.kernel.org/stable/c/10a568010e827108d149779908850afaec898846
- https://git.kernel.org/stable/c/884b44256041ec6b2dcbe8e6a67384d26145cba1
- https://git.kernel.org/stable/c/dd3b237eb7780d65eae296d3d3a70012b6e7a02f
- https://git.kernel.org/stable/c/ff1022c3de46753eb7eba2f6efd990569e66ff95
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64555.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64555
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
