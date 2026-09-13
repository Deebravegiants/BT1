# [M] CVE-2014-8559

## Summary
Severity: Medium
Advisory: CVE-2014-8559
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2014-11-10
Source: https://osv.dev/vulnerability/CVE-2014-8559
Type: osv

## Details
The d_walk function in fs/dcache.c in the Linux kernel through 3.17.2 does not properly maintain the semantics of rename_lock, which allows local users to cause a denial of service (deadlock and system hang) via a crafted application.

## References
- http://lists.opensuse.org/opensuse-security-announce/2015-01/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00015.html
- http://rhn.redhat.com/errata/RHSA-2015-1976.html
- http://rhn.redhat.com/errata/RHSA-2015-1978.html
- http://secunia.com/advisories/62801
- http://www.debian.org/security/2015/dsa-3170
- http://www.openwall.com/lists/oss-security/2014/10/30/7
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2015-2719645.html
- http://www.securityfocus.com/bid/70854
- http://www.securitytracker.com/id/1034051
- http://www.ubuntu.com/usn/USN-2492-1
- http://www.ubuntu.com/usn/USN-2493-1
- http://www.ubuntu.com/usn/USN-2515-1
- http://www.ubuntu.com/usn/USN-2516-1
- http://www.ubuntu.com/usn/USN-2517-1
- http://www.ubuntu.com/usn/USN-2518-1
