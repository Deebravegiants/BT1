# [M] CVE-2016-10069

## Summary
Severity: Medium
Advisory: CVE-2016-10069
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2016-10069
Type: osv

## Details
coders/mat.c in ImageMagick before 6.9.4-5 allows remote attackers to cause a denial of service (application crash) via a mat file with an invalid number of frames.

## References
- http://lists.opensuse.org/opensuse-updates/2017-02/msg00028.html
- http://www.securityfocus.com/bid/95216
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1410507
- https://github.com/ImageMagick/ImageMagick/commit/8a370f9ab120faf182aa160900ba692ba8e2bcf0
