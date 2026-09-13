# [M] CVE-2018-16841

## Summary
Severity: Medium
Advisory: CVE-2018-16841
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-16841
Type: osv

## Details
Samba from version 4.3.0 and before versions 4.7.12, 4.8.7 and 4.9.3 are vulnerable to a denial of service. When configured to accept smart-card authentication, Samba's KDC will call talloc_free() twice on the same memory if the principal in a validly signed certificate does not match the principal in the AS-REQ. This is only possible after authentication with a trusted certificate. talloc is robust against further corruption from a double-free with talloc_free() and directly calls abort(), terminating the KDC process.

## References
- http://www.securityfocus.com/bid/106023
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20181127-0001/
- https://usn.ubuntu.com/3827-1/
- https://usn.ubuntu.com/3827-2/
- https://www.debian.org/security/2018/dsa-4345
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16841
- https://www.samba.org/samba/security/CVE-2018-16841.html
