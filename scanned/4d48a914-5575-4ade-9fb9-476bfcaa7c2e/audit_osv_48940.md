# [M] CVE-2018-18456

## Summary
Severity: Medium
Advisory: CVE-2018-18456
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-18
Source: https://osv.dev/vulnerability/CVE-2018-18456
Type: osv

## Details
The function Object::isName() in Object.h (called from Gfx::opSetFillColorN) in Xpdf 4.00 allows remote attackers to cause a denial of service (stack-based buffer over-read) via a crafted pdf file, as demonstrated by pdftoppm.

## References
- https://forum.xpdfreader.com/viewtopic.php?f=3&t=41217
- https://github.com/TeamSeri0us/pocs/tree/master/xpdf/2018_10_16/pdftoppm
