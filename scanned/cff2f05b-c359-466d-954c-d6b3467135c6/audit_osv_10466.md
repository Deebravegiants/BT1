# [M] CVE-2017-15906

## Summary
Severity: Medium
Advisory: CVE-2017-15906
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2017-10-26
Source: https://osv.dev/vulnerability/CVE-2017-15906
Type: osv

## Details
The process_open function in sftp-server.c in OpenSSH before 7.6 does not properly prevent write operations in readonly mode, which allows attackers to create zero-length files.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- http://www.securityfocus.com/bid/101552
- https://access.redhat.com/errata/RHSA-2018:0980
- https://github.com/openbsd/src/commit/a6981567e8e215acc1ef690c8dbb30f2d9b00a19
- https://lists.debian.org/debian-lts-announce/2018/09/msg00010.html
- https://security.gentoo.org/glsa/201801-05
- https://security.netapp.com/advisory/ntap-20180423-0004/
- https://www.openssh.com/txt/release-7.6
- https://www.oracle.com/security-alerts/cpujan2020.html
