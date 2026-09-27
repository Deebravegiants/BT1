# [H] CVE-2016-2069

## Summary
Severity: High
Advisory: CVE-2016-2069
CVSS: 7.4 (CVSS:3.0/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-04-27
Source: https://osv.dev/vulnerability/CVE-2016-2069
Type: osv

## Details
Race condition in arch/x86/mm/tlb.c in the Linux kernel before 4.4.1 allows local users to gain privileges by triggering access to a paging structure by a different CPU.

## References
- http://www.oracle.com/technetwork/topics/security/linuxbulletinjul2016-3090544.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- http://www.securityfocus.com/bid/81809
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.4.1
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00094.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00045.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00038.html
- http://www.openwall.com/lists/oss-security/2016/01/25/1
- http://www.ubuntu.com/usn/USN-2931-1
- http://rhn.redhat.com/errata/RHSA-2017-0817.html
- http://www.ubuntu.com/usn/USN-2967-1
- http://www.ubuntu.com/usn/USN-2967-2
- http://www.ubuntu.com/usn/USN-2998-1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=71b3c126e61177eb693423f2e18a1914205b165e
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://www.debian.org/security/2016/dsa-3503
- http://www.ubuntu.com/usn/USN-2932-1
- http://www.ubuntu.com/usn/USN-2989-1
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
