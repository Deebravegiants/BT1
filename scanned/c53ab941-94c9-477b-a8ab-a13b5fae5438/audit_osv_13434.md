# [M] CVE-2018-19881

## Summary
Severity: Medium
Advisory: CVE-2018-19881
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-19881
Type: osv

## Details
In Artifex MuPDF 1.14.0, svg/svg-run.c allows remote attackers to cause a denial of service (recursive calls followed by a fitz/xml.c fz_xml_att crash from excessive stack consumption) via a crafted svg file, as demonstrated by mupdf-gl.

## References
- https://bugs.ghostscript.com/show_bug.cgi?id=700342
- https://bugs.ghostscript.com/show_bug.cgi?id=700442
- https://cgit.ghostscript.com/cgi-bin/cgit.cgi/mupdf.git/commit/?id=c8f7e48ff74720a5e984ae19d978a5ab4d5dde5b
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CNJNEX5EW6YH5OARXXSSXW4HHC5PIBSY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SEK2EHVNREJ7XZMFF2MXRWKIF4IBHPNE/
- https://github.com/TeamSeri0us/pocs/tree/master/mupdf/20181203
