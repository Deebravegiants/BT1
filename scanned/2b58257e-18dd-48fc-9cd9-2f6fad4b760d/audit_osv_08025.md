# [M] CVE-2016-10047

## Summary
Severity: Medium
Advisory: CVE-2016-10047
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-23
Source: https://osv.dev/vulnerability/CVE-2016-10047
Type: osv

## Details
Memory leak in the NewXMLTree function in magick/xml-tree.c in ImageMagick before 6.9.4-7 allows remote attackers to cause a denial of service (memory consumption) via a crafted XML file.

## References
- http://www.openwall.com/lists/oss-security/2016/12/26/9
- http://www.securityfocus.com/bid/95182
- https://bugzilla.redhat.com/show_bug.cgi?id=1410449
- https://github.com/ImageMagick/ImageMagick/commit/fc6080f1321fd21e86ef916195cc110b05d9effb
