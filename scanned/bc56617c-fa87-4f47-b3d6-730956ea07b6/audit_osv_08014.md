# [M] CVE-2016-10011

## Summary
Severity: Medium
Advisory: CVE-2016-10011
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-01-05
Source: https://osv.dev/vulnerability/CVE-2016-10011
Type: osv

## Details
authfile.c in sshd in OpenSSH before 7.4 does not properly consider the effects of realloc on buffer contents, which might allow local users to obtain sensitive private-key information by leveraging access to a privilege-separated child process.

## References
- http://www.securityfocus.com/bid/94977
- http://www.securitytracker.com/id/1037490
- http://www.slackware.com/security/viewer.php?l=slackware-security&y=2016&m=slackware-security.647637
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-676336.pdf
- https://lists.debian.org/debian-lts-announce/2018/09/msg00010.html
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbux03818en_us
- https://www.openssh.com/txt/release-7.4
- http://www.openwall.com/lists/oss-security/2016/12/19/2
- https://access.redhat.com/errata/RHSA-2017:2029
- https://security.netapp.com/advisory/ntap-20171130-0002/
- https://github.com/openbsd/src/commit/ac8147a06ed2e2403fb6b9a0c03e618a9333c0e9
