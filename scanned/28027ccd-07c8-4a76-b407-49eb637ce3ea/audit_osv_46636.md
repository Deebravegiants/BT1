# [H] CVE-2014-3687

## Summary
Severity: High
Advisory: CVE-2014-3687
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2014-11-10
Source: https://osv.dev/vulnerability/CVE-2014-3687
Type: osv

## Details
The sctp_assoc_lookup_asconf_ack function in net/sctp/associola.c in the SCTP implementation in the Linux kernel through 3.17.2 allows remote attackers to cause a denial of service (panic) via duplicate ASCONF chunks that trigger an incorrect uncork within the side-effect interpreter.

## References
- http://linux.oracle.com/errata/ELSA-2014-3087.html
- http://linux.oracle.com/errata/ELSA-2014-3088.html
- http://linux.oracle.com/errata/ELSA-2014-3089.html
- http://lists.opensuse.org/opensuse-security-announce/2015-01/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2015-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2015-04/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2015-09/msg00009.html
- http://marc.info/?l=bugtraq&m=142722450701342&w=2
- http://marc.info/?l=bugtraq&m=142722544401658&w=2
- http://rhn.redhat.com/errata/RHSA-2015-0062.html
- http://rhn.redhat.com/errata/RHSA-2015-0115.html
- http://secunia.com/advisories/62428
- http://www.debian.org/security/2014/dsa-3060
- http://www.securityfocus.com/bid/70766
- http://www.ubuntu.com/usn/USN-2417-1
- http://www.ubuntu.com/usn/USN-2418-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1155731
