# [M] CVE-2018-1000801

## Summary
Severity: Medium
Advisory: CVE-2018-1000801
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2018-09-06
Source: https://osv.dev/vulnerability/CVE-2018-1000801
Type: osv

## Details
okular version 18.08 and earlier contains a Directory Traversal vulnerability in function "unpackDocumentArchive(...)" in "core/document.cpp" that can result in Arbitrary file creation on the user workstation. This attack appear to be exploitable via he victim must open a specially crafted Okular archive. This issue appears to have been corrected in version 18.08.1

## References
- https://lists.debian.org/debian-lts-announce/2018/09/msg00027.html
- https://security.gentoo.org/glsa/201811-08
- https://www.debian.org/security/2018/dsa-4303
- https://bugs.kde.org/show_bug.cgi?id=398096
- https://cgit.kde.org/okular.git/commit/?id=8ff7abc14d41906ad978b6bc67e69693863b9d47
