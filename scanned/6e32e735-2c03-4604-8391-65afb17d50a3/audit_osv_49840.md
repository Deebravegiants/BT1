# [M] CVE-2019-19602

## Summary
Severity: Medium
Advisory: CVE-2019-19602
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:L)
Published: 2019-12-05
Source: https://osv.dev/vulnerability/CVE-2019-19602
Type: osv

## Details
fpregs_state_valid in arch/x86/include/asm/fpu/internal.h in the Linux kernel before 5.4.2, when GCC 9 is used, allows context-dependent attackers to cause a denial of service (memory corruption) or possibly have unspecified other impact because of incorrect fpu_fpregs_owner_ctx caching, as demonstrated by mishandling of signal-based non-cooperative preemption in Go 1.14 prereleases on amd64, aka CID-59c4bd853abc.

## References
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://usn.ubuntu.com/4284-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.4.2
- https://bugzilla.kernel.org/show_bug.cgi?id=205663
- https://github.com/golang/go/issues/35777#issuecomment-561935388
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=59c4bd853abcea95eccc167a7d7fd5f1a5f47b98
- https://github.com/torvalds/linux/commit/59c4bd853abcea95eccc167a7d7fd5f1a5f47b98
