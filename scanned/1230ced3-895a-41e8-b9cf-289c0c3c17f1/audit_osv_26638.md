# [M] x86/MCE: Always save CS register on AMD Zen IF Poison errors

## Summary
Severity: Medium
Advisory: CVE-2023-53438
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53438
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/MCE: Always save CS register on AMD Zen IF Poison errors

The Instruction Fetch (IF) units on current AMD Zen-based systems do not
guarantee a synchronous #MC is delivered for poison consumption errors.
Therefore, MCG_STATUS[EIPV|RIPV] will not be set. However, the
microarchitecture does guarantee that the exception is delivered within
the same context. In other words, the exact rIP is not known, but the
context is known to not have changed.

There is no architecturally-defined method to determine this behavior.

The Code Segment (CS) register is always valid on such IF unit poison
errors regardless of the value of MCG_STATUS[EIPV|RIPV].

Add a quirk to save the CS register for poison consumption from the IF
unit banks.

This is needed to properly determine the context of the error.
Otherwise, the severity grading function will assume the context is
IN_KERNEL due to the m->cs value being 0 (the initialized value). This
leads to unnecessary kernel panics on data poison errors due to the
kernel believing the poison consumption occurred in kernel context.

## References
- https://git.kernel.org/stable/c/2e01bdf7203c383e9d8489d9f963c52d6c81e4db
- https://git.kernel.org/stable/c/4240e2ebe67941ce2c4f5c866c3af4b5ac7a0c67
- https://git.kernel.org/stable/c/6eac3965901489ae114a664a78cd2d1415d1af5c
- https://git.kernel.org/stable/c/e6e6a5f50f58fadec397b23064b7e4830292863d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53438.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53438
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
