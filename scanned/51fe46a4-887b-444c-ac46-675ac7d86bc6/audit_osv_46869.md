# [M] CVE-2015-7513

## Summary
Severity: Medium
Advisory: CVE-2015-7513
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-02-08
Source: https://osv.dev/vulnerability/CVE-2015-7513
Type: osv

## Details
arch/x86/kvm/x86.c in the Linux kernel before 4.4 does not reset the PIT counter values during state restoration, which allows guest OS users to cause a denial of service (divide-by-zero error and host OS crash) via a zero value, related to the kvm_vm_ioctl_set_pit and kvm_vm_ioctl_set_pit2 functions.

## References
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0185604c2d82c560dab2f2933a18f797e74ab5a8
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176484.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175792.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/176194.html
- http://www.debian.org/security/2016/dsa-3434
- http://www.openwall.com/lists/oss-security/2016/01/07/2
- http://www.securityfocus.com/bid/79901
- http://www.securitytracker.com/id/1034602
- http://www.ubuntu.com/usn/USN-2886-1
- http://www.ubuntu.com/usn/USN-2887-1
- http://www.ubuntu.com/usn/USN-2887-2
- http://www.ubuntu.com/usn/USN-2888-1
- http://www.ubuntu.com/usn/USN-2889-1
- http://www.ubuntu.com/usn/USN-2889-2
- http://www.ubuntu.com/usn/USN-2890-1
- http://www.ubuntu.com/usn/USN-2890-2
- http://www.ubuntu.com/usn/USN-2890-3
- https://bugzilla.redhat.com/show_bug.cgi?id=1284847
- https://github.com/torvalds/linux/commit/0185604c2d82c560dab2f2933a18f797e74ab5a8
- http://www.openwall.com/lists/oss-security/2016/01/07/2
