# [H] KVM: SVM: Disable AVIC IPI virtualization on Hygon Family 18h (erratum #1235)

## Summary
Severity: High
Advisory: CVE-2026-64172
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64172
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.17.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: SVM: Disable AVIC IPI virtualization on Hygon Family 18h (erratum #1235)

Hygon Family 18h CPUs are derived from AMD Family 17h (Zen1) silicon and
share the same erratum #1235: hardware may read a stale IsRunning=1 bit
during ICR write emulation and silently fail to generate an
AVIC_IPI_FAILURE_TARGET_NOT_RUNNING VM-Exit on the sending vCPU.

The absence of the VM-Exit causes KVM to miss the required wakeup of
blocking target vCPUs, leading to hung vCPUs and unbounded delays in
guest execution.

Extend the existing AMD Family 17h erratum #1235 workaround to also cover
Hygon Family 18h.  With IPI virtualization disabled, KVM never sets
IsRunning=1 in the Physical ID table, so every non-self IPI generates a
VM-Exit and is correctly emulated.

## References
- https://git.kernel.org/stable/c/94ade38f317ea086a181db0e6b69c574b3b70a5e
- https://git.kernel.org/stable/c/9560e6fee887a9594a89fa265b5b9c79b1591803
- https://git.kernel.org/stable/c/9a12fa5213cfc391e0eed63902d3be98f0913765
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64172.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
