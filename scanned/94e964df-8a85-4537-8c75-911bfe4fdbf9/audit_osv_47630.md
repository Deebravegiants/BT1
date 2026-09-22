# [M] CVE-2016-9588

## Summary
Severity: Medium
Advisory: CVE-2016-9588
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2016-9588
Type: osv

## Details
arch/x86/kvm/vmx.c in the Linux kernel through 4.9 mismanages the #BP and #OF exceptions, which allows guest OS users to cause a denial of service (guest OS crash) by declining to handle an exception thrown by an L2 guest.

## References
- https://usn.ubuntu.com/3822-1/
- https://usn.ubuntu.com/3822-2/
- http://www.securityfocus.com/bid/94933
- https://access.redhat.com/errata/RHSA-2017:2077
- http://www.debian.org/security/2017/dsa-3804
- https://access.redhat.com/errata/RHSA-2017:1842
- https://bugzilla.redhat.com/show_bug.cgi?id=1404924
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=ef85b67385436ddc1998f45f1d6a210f935b3388
- http://www.openwall.com/lists/oss-security/2016/12/15/3
- https://github.com/torvalds/linux/commit/ef85b67385436ddc1998f45f1d6a210f935b3388
