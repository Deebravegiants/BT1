# [H] CVE-2019-14934

## Summary
Severity: High
Advisory: CVE-2019-14934
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-08-11
Source: https://osv.dev/vulnerability/CVE-2019-14934
Type: osv

## Details
An issue was discovered in PDFResurrect before 0.18. pdf_load_pages_kids in pdf.c doesn't validate a certain size value, which leads to a malloc failure and out-of-bounds write.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4DBYXYU2VSDJ3NAL54IW2KYD3TZSR33M/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LXN6W5QTNQJ2LFDCQWKYSMMZ3NPUWP3U/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y243C2IFMRFQWHV62JCSHTMQGDDCICNF/
- https://lists.debian.org/debian-lts-announce/2020/12/msg00002.html
- https://github.com/enferex/pdfresurrect/commit/0c4120fffa3dffe97b95c486a120eded82afe8a6
- https://github.com/enferex/pdfresurrect/compare/v0.17...v0.18
