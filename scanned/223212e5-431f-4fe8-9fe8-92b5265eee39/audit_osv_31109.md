# [H] mailbox: th1520: Fix memory corruption due to incorrect array size

## Summary
Severity: High
Advisory: CVE-2024-57983
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57983
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mailbox: th1520: Fix memory corruption due to incorrect array size

The functions th1520_mbox_suspend_noirq and th1520_mbox_resume_noirq are
intended to save and restore the interrupt mask registers in the MBOX
ICU0. However, the array used to store these registers was incorrectly
sized, leading to memory corruption when accessing all four registers.

This commit corrects the array size to accommodate all four interrupt
mask registers, preventing memory corruption during suspend and resume
operations.

## References
- https://git.kernel.org/stable/c/2cd12c7fba59f30369e8647a2b726c7280903304
- https://git.kernel.org/stable/c/db049866943a38bf46a34fa120d526663339d7a5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57983.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57983
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
