# [M] CVE-2021-37750

## Summary
Severity: Medium
Advisory: CVE-2021-37750
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-23
Source: https://osv.dev/vulnerability/CVE-2021-37750
Type: osv

## Details
The Key Distribution Center (KDC) in MIT Kerberos 5 (aka krb5) before 1.18.5 and 1.19.x before 1.19.3 has a NULL pointer dereference in kdc/do_tgs_req.c via a FAST inner body that lacks a server field.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MFCLW7D46E4VCREKKH453T5DA4XOLHU2/
- https://github.com/krb5/krb5/releases
- https://lists.debian.org/debian-lts-announce/2021/09/msg00019.html
- https://security.netapp.com/advisory/ntap-20210923-0002/
- https://web.mit.edu/kerberos/advisories/
- https://www.starwindsoftware.com/security/sw-20220817-0004/
- https://github.com/krb5/krb5/commit/d775c95af7606a51bf79547a94fa52ddd1cb7f49
- https://www.oracle.com/security-alerts/cpujul2022.html
