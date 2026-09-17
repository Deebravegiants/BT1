# [M] CVE-2020-11669

## Summary
Severity: Medium
Advisory: CVE-2020-11669
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-10
Source: https://osv.dev/vulnerability/CVE-2020-11669
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.2 on the powerpc platform. arch/powerpc/kernel/idle_book3s.S does not have save/restore functionality for PNV_POWERSAVE_AMR, PNV_POWERSAVE_UAMOR, and PNV_POWERSAVE_AMOR, aka CID-53a712bae5dd.

## References
- https://usn.ubuntu.com/4368-1/
- https://usn.ubuntu.com/4363-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.2
- https://access.redhat.com/errata/RHSA-2019:3517
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=53a712bae5dd919521a58d7bad773b949358add0
- https://lists.ozlabs.org/pipermail/linuxppc-dev/2020-April/208661.html
- https://lists.ozlabs.org/pipermail/linuxppc-dev/2020-April/208663.html
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00035.html
- https://github.com/torvalds/linux/commit/53a712bae5dd919521a58d7bad773b949358add0
- https://lists.ozlabs.org/pipermail/linuxppc-dev/2020-April/208660.html
- https://security.netapp.com/advisory/ntap-20200430-0001/
