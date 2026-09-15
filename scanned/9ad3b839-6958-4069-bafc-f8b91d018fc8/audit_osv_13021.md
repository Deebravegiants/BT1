# [H] CVE-2018-16877

## Summary
Severity: High
Advisory: CVE-2018-16877
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-18
Source: https://osv.dev/vulnerability/CVE-2018-16877
Type: osv

## Details
A flaw was found in the way pacemaker's client-server authentication was implemented in versions up to and including 2.0.0. A local attacker could use this flaw, and combine it with other IPC weaknesses, to achieve local privilege escalation.

## References
- http://www.securityfocus.com/bid/108042
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3GCWFO7GL6MBU6C4BGFO3P6L77DIBBF3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FY4M4RMIG2POKC6OOFQODGKPRYXHET2F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HR6QUYGML735EI3HEEHYRDW7EG73BUH2/
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00034.html
- https://access.redhat.com/errata/RHSA-2019:1278
- https://access.redhat.com/errata/RHSA-2019:1279
- https://lists.debian.org/debian-lts-announce/2021/01/msg00007.html
- https://security.gentoo.org/glsa/202309-09
- https://usn.ubuntu.com/3952-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16877
- https://github.com/ClusterLabs/pacemaker/pull/1749
