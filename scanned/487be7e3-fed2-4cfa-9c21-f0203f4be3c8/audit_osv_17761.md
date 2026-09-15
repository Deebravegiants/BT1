# [M] CVE-2020-19472

## Summary
Severity: Medium
Advisory: CVE-2020-19472
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2021-07-21
Source: https://osv.dev/vulnerability/CVE-2020-19472
Type: osv

## Details
An issue has been found in function DCTStream::readHuffSym in PDF2JSON 0.70 that allows attackers to cause a Denial of Service due to an invalid read of size 2 .

## References
- https://github.com/flexpaper/pdf2json/issues/33
