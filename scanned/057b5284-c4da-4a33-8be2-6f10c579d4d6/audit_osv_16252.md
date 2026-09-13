# [H] CVE-2019-3829

## Summary
Severity: High
Advisory: CVE-2019-3829
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-03-27
Source: https://osv.dev/vulnerability/CVE-2019-3829
Type: osv

## Details
A vulnerability was found in gnutls versions from 3.5.8 before 3.6.7. A memory corruption (double free) vulnerability in the certificate verification API. Any client or server application that verifies X.509 certificates with GnuTLS 3.5.8 or later is affected.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A3ETBUFBB4G7AITAOUYPGXVMBGVXKUAN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/L7TJIBRJWGWSH6XIO2MXIQ3W6ES4R6I4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WRSOL66LHP4SD3Y2ECJDOGT4K663ECDU/
- https://usn.ubuntu.com/3999-1/
- https://access.redhat.com/errata/RHSA-2019:3600
- https://security.gentoo.org/glsa/201904-14
- https://security.netapp.com/advisory/ntap-20190619-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3829
- https://gitlab.com/gnutls/gnutls/issues/694
- https://www.gnutls.org/security-new.html#GNUTLS-SA-2019-03-27
