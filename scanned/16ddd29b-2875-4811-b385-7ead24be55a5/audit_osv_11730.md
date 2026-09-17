# [M] CVE-2017-9439

## Summary
Severity: Medium
Advisory: CVE-2017-9439
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-06-05
Source: https://osv.dev/vulnerability/CVE-2017-9439
Type: osv

## Details
In ImageMagick 7.0.5-5, a memory leak was found in the function ReadPDBImage in coders/pdb.c, which allows attackers to cause a denial of service via a crafted file.

## References
- http://www.securityfocus.com/bid/98907
- https://github.com/ImageMagick/ImageMagick/issues/460
