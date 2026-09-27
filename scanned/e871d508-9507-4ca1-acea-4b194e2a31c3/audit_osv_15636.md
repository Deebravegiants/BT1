# [H] CVE-2019-18217

## Summary
Severity: High
Advisory: CVE-2019-18217
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-21
Source: https://osv.dev/vulnerability/CVE-2019-18217
Type: osv

## Details
ProFTPD before 1.3.6b and 1.3.7rc before 1.3.7rc2 allows remote unauthenticated denial-of-service due to incorrect handling of overly long commands because main.c in a child process enters an infinite loop.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00009.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-940889.pdf
- https://lists.debian.org/debian-lts-announce/2019/10/msg00036.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NJDQRVZTILBX4BUCTIRKP2WBHDHDCJR5/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RB2FPAWDWXT5ALAFIC5Y3RSEMXSFL6H2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YLRPYEEMQJVAXO2SXRGOQ4HBFEEPCNXG/
- https://seclists.org/bugtraq/2019/Nov/7
- https://github.com/proftpd/proftpd/blob/1.3.6/NEWS
- https://github.com/proftpd/proftpd/blob/1.3.6/RELEASE_NOTES
- https://github.com/proftpd/proftpd/blob/master/NEWS
- https://github.com/proftpd/proftpd/blob/master/RELEASE_NOTES
- https://security.gentoo.org/glsa/202003-35
- https://www.debian.org/security/2019/dsa-4559
- https://github.com/proftpd/proftpd/issues/846
