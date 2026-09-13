# [M] CVE-2017-12444

## Summary
Severity: Medium
Advisory: CVE-2017-12444
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-17
Source: https://osv.dev/vulnerability/CVE-2017-12444
Type: osv

## Details
The mdjvu_bitmap_get_bounding_box function in base/4bitmap.c in minidjvu 0.8 can cause a denial of service (invalid memory read and application crash) via a crafted djvu file.

## References
- http://www.securityfocus.com/bid/100416
- http://seclists.org/fulldisclosure/2017/Aug/15
