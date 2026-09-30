# [M] CVE-2021-46977

## Summary
Severity: Medium
Advisory: CVE-2021-46977
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46977
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: VMX: Disable preemption when probing user return MSRs

Disable preemption when probing a user return MSR via RDSMR/WRMSR.  If
the MSR holds a different value per logical CPU, the WRMSR could corrupt
the host's value if KVM is preempted between the RDMSR and WRMSR, and
then rescheduled on a different CPU.

Opportunistically land the helper in common x86, SVM will use the helper
in a future commit.

## References
- https://git.kernel.org/stable/c/31f29749ee970c251b3a7e5b914108425940d089
- https://git.kernel.org/stable/c/5104d7ffcf24749939bea7fdb5378d186473f890
- https://git.kernel.org/stable/c/5adcdeb57007ccf8ab7ac20bf787ffb6fafb1a94
- https://git.kernel.org/stable/c/e3ea1895df719c4ef87862501bb10d95f4177bed
