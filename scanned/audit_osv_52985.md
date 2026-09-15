# [H] CVE-2022-24106

## Summary
Severity: High
Advisory: CVE-2022-24106
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-30
Source: https://osv.dev/vulnerability/CVE-2022-24106
Type: osv

## Details
In Xpdf prior to 4.04, the DCT (JPEG) decoder was incorrectly allowing the 'interleaved' flag to be changed after the first scan of the image, leading to an unknown integer-related vulnerability in Stream.cc.

## References
- https://dl.xpdfreader.com/xpdf-4.04.tar.gz
- http://www.xpdfreader.com/security-fixes.html
