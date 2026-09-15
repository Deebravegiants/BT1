# [H] CVE-2016-8858

## Summary
Severity: High
Advisory: CVE-2016-8858
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-09
Source: https://osv.dev/vulnerability/CVE-2016-8858
Type: osv

## Details
The kex_input_kexinit function in kex.c in OpenSSH 6.x and 7.x through 7.3 allows remote attackers to cause a denial of service (memory consumption) by sending many duplicate KEXINIT requests.  NOTE: a third party reports that "OpenSSH upstream does not consider this as a security issue."

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- http://www.openwall.com/lists/oss-security/2016/10/19/3
- http://www.openwall.com/lists/oss-security/2016/10/20/1
- http://www.securityfocus.com/bid/93776
- http://www.securitytracker.com/id/1037057
- https://security.FreeBSD.org/advisories/FreeBSD-SA-16:33.openssh.asc
- https://security.gentoo.org/glsa/201612-18
- https://security.netapp.com/advisory/ntap-20180201-0001/
- http://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/kex.c.diff?r1=1.126&r2=1.127&f=h
- http://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/kex.c?rev=1.127&content-type=text/x-cvsweb-markup
- https://bugzilla.redhat.com/show_bug.cgi?id=1384860
- https://ftp.openbsd.org/pub/OpenBSD/patches/6.0/common/013_ssh_kexinit.patch.sig
- https://github.com/openssh/openssh-portable/commit/ec165c392ca54317dbe3064a8c200de6531e89ad
