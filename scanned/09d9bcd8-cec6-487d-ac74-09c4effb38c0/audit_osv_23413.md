# [H] KVM: arm64: Avoid consuming a stale esr value when SError occur

## Summary
Severity: High
Advisory: CVE-2022-48727
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48727
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.22, >=5.16.0 <5.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: Avoid consuming a stale esr value when SError occur

When any exception other than an IRQ occurs, the CPU updates the ESR_EL2
register with the exception syndrome. An SError may also become pending,
and will be synchronised by KVM. KVM notes the exception type, and whether
an SError was synchronised in exit_code.

When an exception other than an IRQ occurs, fixup_guest_exit() updates
vcpu->arch.fault.esr_el2 from the hardware register. When an SError was
synchronised, the vcpu esr value is used to determine if the exception
was due to an HVC. If so, ELR_EL2 is moved back one instruction. This
is so that KVM can process the SError first, and re-execute the HVC if
the guest survives the SError.

But if an IRQ synchronises an SError, the vcpu's esr value is stale.
If the previous non-IRQ exception was an HVC, KVM will corrupt ELR_EL2,
causing an unrelated guest instruction to be executed twice.

Check ARM_EXCEPTION_CODE() before messing with ELR_EL2, IRQs don't
update this register so don't need to check.

## References
- https://git.kernel.org/stable/c/1c71dbc8a179d99dd9bb7e7fc1888db613cf85de
- https://git.kernel.org/stable/c/57e2986c3b25092691a6e3d6ee9168caf8978932
- https://git.kernel.org/stable/c/e1e852746997500f1873f60b954da5f02cc2dba3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48727.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48727
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
