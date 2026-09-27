# [H] CVE-2018-17795

## Summary
Severity: High
Advisory: CVE-2018-17795
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-09-30
Source: https://osv.dev/vulnerability/CVE-2018-17795
Type: osv

## Details
The function t2p_write_pdf in tiff2pdf.c in LibTIFF 4.0.9 and earlier allows remote attackers to cause a denial of service (heap-based buffer overflow and application crash) or possibly have unspecified other impact via a crafted TIFF file, a similar issue to CVE-2017-9935.

## References
- https://github.com/Hack-Me/Pocs_for_Multi_Versions/tree/main/CVE-2018-17795
- http://www.securityfocus.com/bid/105445
- http://bugzilla.maptools.org/show_bug.cgi?id=2816
