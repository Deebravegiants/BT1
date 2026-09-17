# [H] CVE-2019-12957

## Summary
Severity: High
Advisory: CVE-2019-12957
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-06-25
Source: https://osv.dev/vulnerability/CVE-2019-12957
Type: osv

## Details
In Xpdf 4.01.01, a buffer over-read could be triggered in FoFiType1C::convertToType1 in fofi/FoFiType1C.cc when the index number is larger than the charset array bounds. It can, for example, be triggered by sending a crafted PDF document to the pdftops tool. It allows an attacker to use a crafted pdf file to cause Denial of Service or an information leak, or possibly have unspecified other impact.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DJJD7X3ES7ZHJUY2R3DAVCJPV23R64VK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/FWEWFUVITPA3Y6F4A5SJSROKYT7PRH7Q/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TNIJWRYTCLGV35WGIHYTMMOPEEOOTIPT/
- https://forum.xpdfreader.com/viewtopic.php?f=3&t=41813
