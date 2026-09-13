# [M] CVE-2016-10066

## Summary
Severity: Medium
Advisory: CVE-2016-10066
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-03
Source: https://osv.dev/vulnerability/CVE-2016-10066
Type: osv

## Details
Buffer overflow in the ReadVIFFImage function in coders/viff.c in ImageMagick before 6.9.4-5 allows remote attackers to cause a denial of service (application crash) via a crafted file.

## References
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- http://www.securityfocus.com/bid/95217
- https://bugzilla.redhat.com/show_bug.cgi?id=1410491
- https://github.com/ImageMagick/ImageMagick/commit/f6e9d0d9955e85bdd7540b251cd50d598dacc5e6
- https://github.com/ImageMagick/ImageMagick/commit/e45e48b881038487d0bc94d92a16c1537616cc0a
