# [M] CVE-2016-10062

## Summary
Severity: Medium
Advisory: CVE-2016-10062
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2016-10062
Type: osv

## Details
The ReadGROUP4Image function in coders/tiff.c in ImageMagick does not check the return value of the fwrite function, which allows remote attackers to cause a denial of service (application crash) via a crafted file.

## References
- http://www.debian.org/security/2017/dsa-3799
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- http://www.securityfocus.com/bid/95209
- https://github.com/ImageMagick/ImageMagick/issues/196
- https://bugzilla.redhat.com/show_bug.cgi?id=1410473
