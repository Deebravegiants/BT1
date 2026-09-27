# [M] CVE-2018-20685

## Summary
Severity: Medium
Advisory: CVE-2018-20685
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-01-10
Source: https://osv.dev/vulnerability/CVE-2018-20685
Type: osv

## Details
In OpenSSH 7.9, scp.c in the scp client allows remote SSH servers to bypass intended access restrictions via the filename of . or an empty filename. The impact is modifying the permissions of the target directory on the client side.

## References
- http://www.securityfocus.com/bid/106531
- https://access.redhat.com/errata/RHSA-2019:3702
- https://lists.debian.org/debian-lts-announce/2019/03/msg00030.html
- https://security.gentoo.org/glsa/201903-16
- https://security.gentoo.org/glsa/202007-53
- https://security.netapp.com/advisory/ntap-20190215-0001/
- https://usn.ubuntu.com/3885-1/
- https://www.debian.org/security/2019/dsa-4387
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/scp.c.diff?r1=1.197&r2=1.198&f=h
- https://github.com/openssh/openssh-portable/commit/6010c0303a422a9c5fa8860c061bf7105eb7f8b2
- https://sintonen.fi/advisories/scp-client-multiple-vulnerabilities.txt
- https://www.oracle.com/technetwork/security-advisory/cpuapr2019-5072813.html
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
