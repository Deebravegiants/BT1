# [H] CVE-2019-3863

## Summary
Severity: High
Advisory: CVE-2019-3863
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-03-25
Source: https://osv.dev/vulnerability/CVE-2019-3863
Type: osv

## Details
A flaw was found in libssh2 before 1.8.1 creating a vulnerability on the SSH client side. A server could send a multiple keyboard interactive response messages whose total length are greater than unsigned char max characters. This value is used by the SSH client as an index to copy memory causing in an out of bounds memory write error.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5DK6VO2CEUTAJFYIKWNZKEKYMYR3NO2O/
- https://seclists.org/bugtraq/2019/Apr/25
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00040.html
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00003.html
- https://access.redhat.com/errata/RHSA-2019:0679
- https://access.redhat.com/errata/RHSA-2019:1175
- https://access.redhat.com/errata/RHSA-2019:1652
- https://access.redhat.com/errata/RHSA-2019:1791
- https://access.redhat.com/errata/RHSA-2019:1943
- https://access.redhat.com/errata/RHSA-2019:2399
- https://lists.debian.org/debian-lts-announce/2019/03/msg00032.html
- https://security.netapp.com/advisory/ntap-20190327-0005/
- https://www.debian.org/security/2019/dsa-4431
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-3863
- https://www.libssh2.org/CVE-2019-3863.html
