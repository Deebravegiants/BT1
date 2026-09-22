# [H] CVE-2021-32919

## Summary
Severity: High
Advisory: CVE-2021-32919
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-05-13
Source: https://osv.dev/vulnerability/CVE-2021-32919
Type: osv

## Details
An issue was discovered in Prosody before 0.11.9. The undocumented dialback_without_dialback option in mod_dialback enables an experimental feature for server-to-server authentication. It does not correctly authenticate remote server certificates, allowing a remote server to impersonate another server (when this option is enabled).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GUN63AHEWB2WRROJHU3BVJRWLONCT2B7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LWJ2DG2DFJOEFEWOUN26IMYYWGSA2ZEE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6MFFBZWXKPZEVZNQSVJNCUE7WRF3T7DG/
- https://security.gentoo.org/glsa/202105-15
- https://www.debian.org/security/2021/dsa-4916
- http://www.openwall.com/lists/oss-security/2021/05/13/1
- http://www.openwall.com/lists/oss-security/2021/05/14/2
- https://blog.prosody.im/prosody-0.11.9-released/
