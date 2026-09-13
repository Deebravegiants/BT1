# [M] CVE-2016-10071

## Summary
Severity: Medium
Advisory: CVE-2016-10071
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2016-10071
Type: osv

## Details
coders/mat.c in ImageMagick before 6.9.4-0 allows remote attackers to cause a denial of service (out-of-bounds read and application crash) via a crafted mat file.

## References
- http://www.securityfocus.com/bid/95222
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1410513
- https://github.com/ImageMagick/ImageMagick/commit/1bc1fd0ff8c555841c78829217ac81fa0598255d
- https://github.com/ImageMagick/ImageMagick/commit/f3b483e8b054c50149912523b4773687e18afe25
