# [C] CVE-2016-6525

## Summary
Severity: Critical
Advisory: CVE-2016-6525
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-22
Source: https://osv.dev/vulnerability/CVE-2016-6525
Type: osv

## Details
Heap-based buffer overflow in the pdf_load_mesh_params function in pdf/pdf-shade.c in MuPDF allows remote attackers to cause a denial of service (crash) or execute arbitrary code via a large decode array.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=39b0f07dd960f34e7e6bf230ffc3d87c41ef0f2e
- http://www.debian.org/security/2016/dsa-3655
- http://www.securityfocus.com/bid/92266
- https://security.gentoo.org/glsa/201702-12
- http://bugs.ghostscript.com/show_bug.cgi?id=696954
- http://www.openwall.com/lists/oss-security/2016/08/03/8
