# [M] CVE-2016-10070

## Summary
Severity: Medium
Advisory: CVE-2016-10070
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/CVE-2016-10070
Type: osv

## Details
Heap-based buffer overflow in the CalcMinMax function in coders/mat.c in ImageMagick before 6.9.4-0 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted mat file.

## References
- http://lists.opensuse.org/opensuse-updates/2017-02/msg00028.html
- http://lists.opensuse.org/opensuse-updates/2017-02/msg00031.html
- http://www.securityfocus.com/bid/95221
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- https://bugs.launchpad.net/ubuntu/+source/imagemagick/+bug/1545366
- https://bugzilla.redhat.com/show_bug.cgi?id=1410510
- https://github.com/ImageMagick/ImageMagick/commit/a6240a163cb787909703d9fc649cf861f60ddd7c
- https://github.com/ImageMagick/ImageMagick/commit/b173a352397877775c51c9a0e9d59eb6ce24c455
