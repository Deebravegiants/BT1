# [M] CVE-2014-3690

## Summary
Severity: Medium
Advisory: CVE-2014-3690
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2014-11-10
Source: https://osv.dev/vulnerability/CVE-2014-3690
Type: osv

## Details
arch/x86/kvm/vmx.c in the KVM subsystem in the Linux kernel before 3.17.2 on Intel processors does not ensure that the value in the CR4 control register remains the same after a VM entry, which allows host OS users to kill arbitrary processes or cause a denial of service (system disruption) by leveraging /dev/kvm access, as demonstrated by PR_SET_TSC prctl calls within a modified copy of QEMU.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-01/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00015.html
- http://rhn.redhat.com/errata/RHSA-2015-0290.html
- http://rhn.redhat.com/errata/RHSA-2015-0782.html
- http://rhn.redhat.com/errata/RHSA-2015-0864.html
- http://secunia.com/advisories/60174
- http://www.debian.org/security/2014/dsa-3060
- http://www.kernel.org/pub/linux/kernel/v3.x/ChangeLog-3.17.2
- http://www.mandriva.com/security/advisories?name=MDVSA-2015:058
- http://www.openwall.com/lists/oss-security/2014/10/21/4
- http://www.openwall.com/lists/oss-security/2014/10/29/7
- http://www.securityfocus.com/bid/70691
- http://www.ubuntu.com/usn/USN-2417-1
- http://www.ubuntu.com/usn/USN-2418-1
- http://www.ubuntu.com/usn/USN-2419-1
- http://www.ubuntu.com/usn/USN-2420-1
- http://www.ubuntu.com/usn/USN-2421-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1153322
