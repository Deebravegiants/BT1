# [H] CVE-2015-7508

## Summary
Severity: High
Advisory: CVE-2015-7508
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2015-7508
Type: osv

## Details
Heap-based buffer overflow in the bmp_decode_rle function in libnsbmp.c in Libnsbmp 0.1.2 allows context-dependent attackers to cause a denial of service (application crash) or possibly execute arbitrary code via the last row of RLE data in a crafted BMP file.

## References
- http://seclists.org/fulldisclosure/2015/Dec/73
- http://www.securityfocus.com/archive/1/archive/1/537132/100/0/threaded
- http://seclists.org/fulldisclosure/2015/Dec/73
- http://seclists.org/fulldisclosure/2015/Dec/73
- http://www.securityfocus.com/archive/1/archive/1/537132/100/0/threaded
