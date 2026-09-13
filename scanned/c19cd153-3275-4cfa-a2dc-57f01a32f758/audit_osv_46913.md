# [H] CVE-2015-7978

## Summary
Severity: High
Advisory: CVE-2015-7978
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-01-30
Source: https://osv.dev/vulnerability/CVE-2015-7978
Type: osv

## Details
NTP before 4.2.8p6 and 4.3.0 before 4.3.90 allows a remote attackers to cause a denial of service (stack exhaustion) via an ntpdc relist command, which triggers recursive traversal of the restriction list.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/177507.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/176434.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00059.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00048.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00042.html
- http://lists.opensuse.org/opensuse-updates/2016-05/msg00114.html
- http://rhn.redhat.com/errata/RHSA-2016-0780.html
- http://rhn.redhat.com/errata/RHSA-2016-2583.html
- http://support.ntp.org/bin/view/Main/SecurityNotice#April_2016_NTP_4_2_8p7_Security
- http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20160127-ntpd
- http://www.debian.org/security/2016/dsa-3629
- http://www.securityfocus.com/bid/81962
- http://www.securitytracker.com/id/1034782
- http://www.ubuntu.com/usn/USN-3096-1
- https://bto.bluecoat.com/security-advisory/sa113
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:09.ntp.asc
