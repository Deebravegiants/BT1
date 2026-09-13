# [M] CVE-2014-3646

## Summary
Severity: Medium
Advisory: CVE-2014-3646
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2014-11-10
Source: https://osv.dev/vulnerability/CVE-2014-3646
Type: osv

## Details
arch/x86/kvm/vmx.c in the KVM subsystem in the Linux kernel through 3.17.2 does not have an exit handler for the INVVPID instruction, which allows guest OS users to cause a denial of service (guest OS crash) via a crafted application.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://rhn.redhat.com/errata/RHSA-2015-0126.html
- http://rhn.redhat.com/errata/RHSA-2015-0284.html
- http://www.debian.org/security/2014/dsa-3060
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- http://www.ubuntu.com/usn/USN-2394-1
- http://www.ubuntu.com/usn/USN-2417-1
- http://www.ubuntu.com/usn/USN-2418-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1144825
- https://github.com/torvalds/linux/commit/a642fc305053cc1c6e47e4f4df327895747ab485
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1144825
- https://github.com/torvalds/linux/commit/a642fc305053cc1c6e47e4f4df327895747ab485
- https://bugzilla.redhat.com/show_bug.cgi?id=1144825
- http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git%3Ba=commit%3Bh=a642fc305053cc1c6e47e4f4df327895747ab485
