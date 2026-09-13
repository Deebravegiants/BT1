# [M] CVE-2016-10220

## Summary
Severity: Medium
Advisory: CVE-2016-10220
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-04-03
Source: https://osv.dev/vulnerability/CVE-2016-10220
Type: osv

## Details
The gs_makewordimagedevice function in base/gsdevmem.c in Artifex Software, Inc. Ghostscript 9.20 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via a crafted file that is mishandled in the PDF Transparency module.

## References
- http://www.debian.org/security/2017/dsa-3838
- https://security.gentoo.org/glsa/201708-06
- http://www.ghostscript.com/cgi-bin/findgit.cgi?daf85701dab05f17e924a48a81edc9195b4a04e8
- https://bugs.ghostscript.com/show_bug.cgi?id=697450
