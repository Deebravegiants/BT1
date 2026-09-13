# [H] CVE-2019-9278

## Summary
Severity: High
Advisory: CVE-2019-9278
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-09-27
Source: https://osv.dev/vulnerability/CVE-2019-9278
Type: osv

## Details
In libexif, there is a possible out of bounds write due to an integer overflow. This could lead to remote escalation of privilege in the media content provider with no additional execution privileges needed. User interaction is needed for exploitation. Product: AndroidVersions: Android-10Android ID: A-112537774

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VA5BPQLOFXIZOOJHBYDU635Z5KLUMTDD/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MO2VTHD7OLPJDCJBHKUQTBAHZOBBCF6X/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00017.html
- https://seclists.org/bugtraq/2020/Feb/9
- https://source.android.com/security/bulletin/android-10
- https://usn.ubuntu.com/4277-1/
- https://lists.debian.org/debian-lts-announce/2020/02/msg00007.html
- https://security.gentoo.org/glsa/202007-05
- https://www.debian.org/security/2020/dsa-4618
- https://github.com/libexif/libexif/commit/75aa73267fdb1e0ebfbc00369e7312bac43d0566
- https://github.com/libexif/libexif/issues/26
- http://www.openwall.com/lists/oss-security/2019/11/07/1
- http://www.openwall.com/lists/oss-security/2019/10/25/17
- http://www.openwall.com/lists/oss-security/2019/10/27/1
