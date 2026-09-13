# [H] CVE-2016-2118

## Summary
Severity: High
Advisory: CVE-2016-2118
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-04-12
Source: https://osv.dev/vulnerability/CVE-2016-2118
Type: osv

## Details
The MS-SAMR and MS-LSAD protocol implementations in Samba 3.x and 4.x before 4.2.11, 4.3.x before 4.3.8, and 4.4.x before 4.4.2 mishandle DCERPC connections, which allows man-in-the-middle attackers to perform protocol-downgrade attacks and impersonate users by modifying the client-server data stream, aka "BADLOCK."

## References
- http://badlock.org/
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182185.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182272.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-April/182288.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00024.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00042.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00047.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00048.html
- http://rhn.redhat.com/errata/RHSA-2016-0611.html
- http://rhn.redhat.com/errata/RHSA-2016-0612.html
- http://rhn.redhat.com/errata/RHSA-2016-0613.html
- http://rhn.redhat.com/errata/RHSA-2016-0614.html
- http://rhn.redhat.com/errata/RHSA-2016-0618.html
- http://rhn.redhat.com/errata/RHSA-2016-0619.html
- http://rhn.redhat.com/errata/RHSA-2016-0620.html
- http://rhn.redhat.com/errata/RHSA-2016-0621.html
