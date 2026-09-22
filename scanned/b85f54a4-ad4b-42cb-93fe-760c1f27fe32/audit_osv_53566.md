# [H] CVE-2023-0045

## Summary
Severity: High
Advisory: CVE-2023-0045
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-25
Source: https://osv.dev/vulnerability/CVE-2023-0045
Type: osv

## Details
The current implementation of the prctl syscall does not issue an IBPB immediately during the syscall. The ib_prctl_set  function updates the Thread Information Flags (TIFs) for the task and updates the SPEC_CTRL MSR on the function __speculation_ctrl_update, but the IBPB is only issued on the next schedule, when the TIF bits are checked. This leaves the victim vulnerable to values already injected on the BTB, prior to the prctl syscall.  The patch that added the support for the conditional mitigation via prctl (ib_prctl_set) dates back to the kernel 4.9.176.

We recommend upgrading past commit a664ec9158eeddd75121d39c9a0758016097fa96

## References
- https://lists.debian.org/debian-lts-announce/2023/05/msg00006.html
- https://security.netapp.com/advisory/ntap-20230714-0001/
- https://lists.debian.org/debian-lts-announce/2023/05/msg00005.html
- https://git.kernel.org/tip/a664ec9158eeddd75121d39c9a0758016097fa96
- https://github.com/google/security-research/security/advisories/GHSA-9x5g-vmxf-4qj8
