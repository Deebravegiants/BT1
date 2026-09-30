# [H] CVE-2016-8687

## Summary
Severity: High
Advisory: CVE-2016-8687
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-15
Source: https://osv.dev/vulnerability/CVE-2016-8687
Type: osv

## Details
Stack-based buffer overflow in the safe_fprintf function in tar/util.c in libarchive 3.2.1 allows remote attackers to cause a denial of service via a crafted non-printable multibyte character in a filename.

## References
- http://www.securitytracker.com/id/1037668
- https://lists.debian.org/debian-lts-announce/2018/11/msg00037.html
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00027.html
- http://www.securityfocus.com/bid/93781
- http://www.openwall.com/lists/oss-security/2016/10/16/11
- https://blogs.gentoo.org/ago/2016/09/11/libarchive-bsdtar-stack-based-buffer-overflow-in-bsdtar_expand_char-util-c/
- https://bugzilla.redhat.com/show_bug.cgi?id=1377926
- https://github.com/libarchive/libarchive/commit/e37b620fe8f14535d737e89a4dcabaed4517bf1a
- https://security.gentoo.org/glsa/201701-03
