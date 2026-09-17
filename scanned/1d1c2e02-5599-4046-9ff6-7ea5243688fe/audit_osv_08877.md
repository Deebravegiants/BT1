# [H] CVE-2016-6515

## Summary
Severity: High
Advisory: CVE-2016-6515
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-08-07
Source: https://osv.dev/vulnerability/CVE-2016-6515
Type: osv

## Details
The auth_password function in auth-passwd.c in sshd in OpenSSH before 7.3 does not limit password lengths for password authentication, which allows remote attackers to cause a denial of service (crypt CPU consumption) via a long string.

## References
- http://packetstormsecurity.com/files/140070/OpenSSH-7.2-Denial-Of-Service.html
- http://www.securityfocus.com/bid/92212
- http://www.securitytracker.com/id/1036487
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://cert-portal.siemens.com/productcert/pdf/ssa-676336.pdf
- https://lists.debian.org/debian-lts-announce/2018/09/msg00010.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X2L6RW34VFNXYNVVN2CN73YAGJ5VMTFU/
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03779en_us
- https://www.exploit-db.com/exploits/40888/
- http://openwall.com/lists/oss-security/2016/08/01/2
- http://www.oracle.com/technetwork/security-advisory/cpuoct2017-3236626.html
- https://access.redhat.com/errata/RHSA-2017:2029
- https://security.FreeBSD.org/advisories/FreeBSD-SA-17:06.openssh.asc
- https://security.netapp.com/advisory/ntap-20171130-0003/
- https://github.com/openssh/openssh-portable/commit/fcd135c9df440bcd2d5870405ad3311743d78d97
