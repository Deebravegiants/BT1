# [M] CVE-2021-32921

## Summary
Severity: Medium
Advisory: CVE-2021-32921
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-32921
Type: osv

## Details
An issue was discovered in Prosody before 0.11.9. It does not use a constant-time algorithm for comparing certain secret strings when running under Lua 5.2 or later. This can potentially be used in a timing attack to reveal the contents of secret strings to an attacker.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GUN63AHEWB2WRROJHU3BVJRWLONCT2B7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LWJ2DG2DFJOEFEWOUN26IMYYWGSA2ZEE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6MFFBZWXKPZEVZNQSVJNCUE7WRF3T7DG/
- https://www.debian.org/security/2021/dsa-4916
- http://www.openwall.com/lists/oss-security/2021/05/14/2
- https://blog.prosody.im/prosody-0.11.9-released/
- https://lists.debian.org/debian-lts-announce/2021/06/msg00016.html
- https://security.gentoo.org/glsa/202105-15
- http://www.openwall.com/lists/oss-security/2021/05/13/1
- https://lists.debian.org/debian-lts-announce/2021/06/msg00018.html
