# [M] CVE-2019-3824

## Summary
Severity: Medium
Advisory: CVE-2019-3824
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-06
Source: https://osv.dev/vulnerability/CVE-2019-3824
Type: osv

## Details
A flaw was found in the way an LDAP search expression could crash the shared LDAP server process of a samba AD DC in samba before version 4.10. An authenticated user, having read permissions on the LDAP server, could use this flaw to cause denial of service.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00035.html
- http://www.securityfocus.com/bid/107347
- https://lists.debian.org/debian-lts-announce/2019/03/msg00000.html
- https://security.netapp.com/advisory/ntap-20190226-0001/
- https://usn.ubuntu.com/3895-1/
- https://www.debian.org/security/2019/dsa-4397
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3824
- https://bugzilla.samba.org/show_bug.cgi?id=13773
