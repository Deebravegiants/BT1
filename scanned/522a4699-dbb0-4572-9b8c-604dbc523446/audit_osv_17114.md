# [M] CVE-2020-12659

## Summary
Severity: Medium
Advisory: CVE-2020-12659
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-05
Source: https://osv.dev/vulnerability/CVE-2020-12659
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.6.7. xdp_umem_reg in net/xdp/xdp_umem.c has an out-of-bounds write (by a user with the CAP_NET_ADMIN capability) because of a lack of headroom validation.

## References
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://usn.ubuntu.com/4389-1/
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.6.7
- https://usn.ubuntu.com/4387-1/
- https://usn.ubuntu.com/4388-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00022.html
- https://bugzilla.kernel.org/show_bug.cgi?id=207225
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=99e3a236dd43d06c65af0a2ef9cb44306aef6e02
- https://github.com/torvalds/linux/commit/99e3a236dd43d06c65af0a2ef9cb44306aef6e02
