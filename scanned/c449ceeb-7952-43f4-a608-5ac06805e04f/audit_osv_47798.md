# [M] CVE-2017-12445

## Summary
Severity: Medium
Advisory: CVE-2017-12445
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-17
Source: https://osv.dev/vulnerability/CVE-2017-12445
Type: osv

## Details
The JB2BitmapCoder::code_row_by_refinement function in jb2/bmpcoder.cpp in minidjvu 0.8 can cause a denial of service (invalid memory read and application crash) via a crafted djvu file.

## References
- http://www.securityfocus.com/bid/100423
- http://seclists.org/fulldisclosure/2017/Aug/15
