# [M] CVE-2014-3611

## Summary
Severity: Medium
Advisory: CVE-2014-3611
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2014-11-10
Source: https://osv.dev/vulnerability/CVE-2014-3611
Type: osv

## Details
Race condition in the __kvm_migrate_pit_timer function in arch/x86/kvm/i8254.c in the KVM subsystem in the Linux kernel through 3.17.2 allows guest OS users to cause a denial of service (host OS crash) by leveraging incorrect PIT emulation.

## References
- http://rhn.redhat.com/errata/RHSA-2015-0126.html
- http://rhn.redhat.com/errata/RHSA-2015-0284.html
- http://rhn.redhat.com/errata/RHSA-2015-0869.html
- http://www.debian.org/security/2014/dsa-3060
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- http://www.ubuntu.com/usn/USN-2394-1
- http://www.ubuntu.com/usn/USN-2417-1
- http://www.ubuntu.com/usn/USN-2418-1
- http://www.ubuntu.com/usn/USN-2491-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1144878
- https://github.com/torvalds/linux/commit/2febc839133280d5a5e8e1179c94ea674489dae2
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1144878
- https://github.com/torvalds/linux/commit/2febc839133280d5a5e8e1179c94ea674489dae2
- https://bugzilla.redhat.com/show_bug.cgi?id=1144878
- http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git%3Ba=commit%3Bh=2febc839133280d5a5e8e1179c94ea674489dae2
