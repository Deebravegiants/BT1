# [H] CVE-2019-16905

## Summary
Severity: High
Advisory: CVE-2019-16905
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/CVE-2019-16905
Type: osv

## Details
OpenSSH 7.7 through 7.9 and 8.x before 8.1, when compiled with an experimental key type, has a pre-authentication integer overflow if a client or server is configured to use a crafted XMSS key. This leads to memory corruption and local code execution because of an error in the XMSS key parsing algorithm. NOTE: the XMSS implementation is considered experimental in all released OpenSSH versions, and there is no supported way to enable it when building portable OpenSSH.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-412672.pdf
- https://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/sshkey-xmss.c
- https://security.gentoo.org/glsa/201911-01
- https://security.netapp.com/advisory/ntap-20191024-0003/
- https://www.openssh.com/releasenotes.html
- https://www.openwall.com/lists/oss-security/2019/10/09/1
- https://bugzilla.suse.com/show_bug.cgi?id=1153537
- https://cvsweb.openbsd.org/cgi-bin/cvsweb/src/usr.bin/ssh/sshkey-xmss.c.diff?r1=1.5&r2=1.6&f=h
- https://ssd-disclosure.com/archives/4033/ssd-advisory-openssh-pre-auth-xmss-integer-overflow
