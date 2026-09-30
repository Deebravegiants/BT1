# [M] CVE-2018-19882

## Summary
Severity: Medium
Advisory: CVE-2018-19882
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-06
Source: https://osv.dev/vulnerability/CVE-2018-19882
Type: osv

## Details
In Artifex MuPDF 1.14.0, the svg_run_image function in svg/svg-run.c allows remote attackers to cause a denial of service (href_att NULL pointer dereference and application crash) via a crafted svg file, as demonstrated by mupdf-gl.

## References
- http://www.ghostscript.com/cgi-bin/findgit.cgi?a7f7d91cdff8d303c11d458fa8b802776f73c8cc
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CNJNEX5EW6YH5OARXXSSXW4HHC5PIBSY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SEK2EHVNREJ7XZMFF2MXRWKIF4IBHPNE/
- https://bugs.ghostscript.com/show_bug.cgi?id=700342
- https://github.com/TeamSeri0us/pocs/tree/master/mupdf/20181203
