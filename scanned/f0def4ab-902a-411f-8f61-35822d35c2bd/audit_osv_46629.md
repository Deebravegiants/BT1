# [M] CVE-2014-3610

## Summary
Severity: Medium
Advisory: CVE-2014-3610
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2014-11-10
Source: https://osv.dev/vulnerability/CVE-2014-3610
Type: osv

## Details
The WRMSR processing functionality in the KVM subsystem in the Linux kernel through 3.17.2 does not properly handle the writing of a non-canonical address to a model-specific register, which allows guest OS users to cause a denial of service (host OS crash) by leveraging guest OS privileges, related to the wrmsr_interception function in arch/x86/kvm/svm.c and the handle_wrmsr function in arch/x86/kvm/vmx.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://rhn.redhat.com/errata/RHSA-2015-0869.html
- http://www.debian.org/security/2014/dsa-3060
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- http://www.securityfocus.com/bid/70742
- http://www.ubuntu.com/usn/USN-2394-1
- http://www.ubuntu.com/usn/USN-2417-1
- http://www.ubuntu.com/usn/USN-2418-1
- http://www.ubuntu.com/usn/USN-2491-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1144883
- https://github.com/torvalds/linux/commit/854e8bb1aa06c578c2c9145fa6bfe3680ef63b23
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- https://github.com/torvalds/linux/commit/854e8bb1aa06c578c2c9145fa6bfe3680ef63b23
- http://www.openwall.com/lists/oss-security/2014/10/24/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1144883
- https://github.com/torvalds/linux/commit/854e8bb1aa06c578c2c9145fa6bfe3680ef63b23
- https://bugzilla.redhat.com/show_bug.cgi?id=1144883
