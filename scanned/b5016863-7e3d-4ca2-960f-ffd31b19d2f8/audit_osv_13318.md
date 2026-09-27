# [M] CVE-2018-19210

## Summary
Severity: Medium
Advisory: CVE-2018-19210
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19210
Type: osv

## Details
In LibTIFF 4.0.9, there is a NULL pointer dereference in the TIFFWriteDirectorySec function in tif_dirwrite.c that will lead to a denial of service attack, as demonstrated by tiffset.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-04/msg00041.html
- http://packetstormsecurity.com/files/155095/Slackware-Security-Advisory-libtiff-Updates.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/C6IL2QFKE6MGVUTOPU2UUWITTE36KRDF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TX5UEYHGMTNEHJB4FHE7HCJ75UQDNKGB/
- https://seclists.org/bugtraq/2019/Nov/5
- http://www.securityfocus.com/bid/105932
- https://lists.debian.org/debian-lts-announce/2019/02/msg00026.html
- https://security.gentoo.org/glsa/202003-25
- https://usn.ubuntu.com/3906-1/
- https://www.debian.org/security/2020/dsa-4670
- http://bugzilla.maptools.org/show_bug.cgi?id=2820
