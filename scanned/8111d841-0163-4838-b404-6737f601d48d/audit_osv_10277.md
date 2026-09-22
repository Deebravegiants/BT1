# [H] CVE-2017-14686

## Summary
Severity: High
Advisory: CVE-2017-14686
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-09-22
Source: https://osv.dev/vulnerability/CVE-2017-14686
Type: osv

## Details
Artifex MuPDF 1.11 allows attackers to execute arbitrary code or cause a denial of service via a crafted .xps file, related to a "User Mode Write AV near NULL starting at wow64!Wow64NotifyDebugger+0x000000000000001d" on Windows. This occurs because read_zip_dir_imp in fitz/unzip.c does not check whether size fields in a ZIP entry are negative numbers.

## References
- http://git.ghostscript.com/?p=mupdf.git%3Bh=0f0fbc07d9be31f5e83ec5328d7311fdfd8328b1
- http://www.debian.org/security/2017/dsa-4006
- https://github.com/wlinzi/security_advisories/tree/master/CVE-2017-14686
- https://bugs.ghostscript.com/show_bug.cgi?id=698540
