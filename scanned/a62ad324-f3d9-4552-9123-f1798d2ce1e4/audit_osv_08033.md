# [H] CVE-2016-10067

## Summary
Severity: High
Advisory: CVE-2016-10067
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2016-10067
Type: osv

## Details
magick/memory.c in ImageMagick before 6.9.4-5 allows remote attackers to cause a denial of service (application crash) via vectors involving "too many exceptions," which trigger a buffer overflow.

## References
- http://www.securityfocus.com/bid/95220
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1410494
- https://github.com/ImageMagick/ImageMagick/commit/0474237508f39c4f783208123431815f1ededb76
