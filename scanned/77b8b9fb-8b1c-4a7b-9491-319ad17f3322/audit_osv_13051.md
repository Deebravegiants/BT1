# [H] CVE-2018-17101

## Summary
Severity: High
Advisory: CVE-2018-17101
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-16
Source: https://osv.dev/vulnerability/CVE-2018-17101
Type: osv

## Details
An issue was discovered in LibTIFF 4.0.9. There are two out-of-bounds writes in cpTags in tools/tiff2bw.c and tools/pal2rgb.c, which can cause a denial of service (application crash) or possibly have unspecified other impact via a crafted image file.

## References
- https://usn.ubuntu.com/3906-2/
- http://www.securityfocus.com/bid/105370
- https://access.redhat.com/errata/RHSA-2019:2053
- https://lists.debian.org/debian-lts-announce/2018/10/msg00019.html
- https://usn.ubuntu.com/3864-1/
- https://www.debian.org/security/2018/dsa-4349
- http://bugzilla.maptools.org/show_bug.cgi?id=2807
- https://gitlab.com/libtiff/libtiff/merge_requests/33/diffs?commit_id=f1b94e8a3ba49febdd3361c0214a1d1149251577
