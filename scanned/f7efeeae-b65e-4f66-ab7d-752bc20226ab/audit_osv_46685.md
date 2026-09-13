# [H] CVE-2014-9322

## Summary
Severity: High
Advisory: CVE-2014-9322
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2014-12-17
Source: https://osv.dev/vulnerability/CVE-2014-9322
Type: osv

## Details
arch/x86/kernel/entry_64.S in the Linux kernel before 3.17.5 does not properly handle faults associated with the Stack Segment (SS) segment register, which allows local users to gain privileges by triggering an IRET instruction that leads to access to a GS Base address from the wrong space.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00020.html
- http://marc.info/?l=bugtraq&m=142722450701342&w=2
- http://marc.info/?l=bugtraq&m=142722544401658&w=2
- http://rhn.redhat.com/errata/RHSA-2014-1998.html
- http://rhn.redhat.com/errata/RHSA-2014-2008.html
- http://rhn.redhat.com/errata/RHSA-2014-2028.html
- http://rhn.redhat.com/errata/RHSA-2014-2031.html
- http://rhn.redhat.com/errata/RHSA-2015-0009.html
- http://secunia.com/advisories/62336
- http://source.android.com/security/bulletin/2016-04-02.html
- http://www.exploit-db.com/exploits/36266
- http://www.openwall.com/lists/oss-security/2014/12/15/6
- http://www.ubuntu.com/usn/USN-2491-1
- http://www.zerodayinitiative.com/advisories/ZDI-16-170
- https://bugzilla.redhat.com/show_bug.cgi?id=1172806
- https://github.com/torvalds/linux/commit/6f442be2fb22be02cafa606f1769fa1e6f894441
- https://help.joyent.com/entries/98788667-Security-Advisory-ZDI-CAN-3263-ZDI-CAN-3284-and-ZDI-CAN-3364-Vulnerabilities
- https://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.17.5
