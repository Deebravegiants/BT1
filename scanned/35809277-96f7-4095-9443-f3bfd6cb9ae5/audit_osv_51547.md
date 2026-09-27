# [M] CVE-2021-32917

## Summary
Severity: Medium
Advisory: CVE-2021-32917
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-32917
Type: osv

## Details
An issue was discovered in Prosody before 0.11.9. The proxy65 component allows open access by default, even if neither of the users has an XMPP account on the local server, allowing unrestricted use of the server's bandwidth.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GUN63AHEWB2WRROJHU3BVJRWLONCT2B7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LWJ2DG2DFJOEFEWOUN26IMYYWGSA2ZEE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6MFFBZWXKPZEVZNQSVJNCUE7WRF3T7DG/
- https://security.gentoo.org/glsa/202105-15
- http://www.openwall.com/lists/oss-security/2021/05/13/1
- https://blog.prosody.im/prosody-0.11.9-released/
- https://www.debian.org/security/2021/dsa-4916
- http://www.openwall.com/lists/oss-security/2021/05/14/2
- https://lists.debian.org/debian-lts-announce/2021/06/msg00016.html
