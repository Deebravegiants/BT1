# [H] CVE-2018-18315

## Summary
Severity: High
Advisory: CVE-2018-18315
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-10-15
Source: https://osv.dev/vulnerability/CVE-2018-18315
Type: osv

## Details
com/mossle/cdn/CdnController.java in lemon 1.9.0 allows attackers to upload arbitrary files because the copyMultipartFileToFile method in CdnUtils only checks for a ../ substring, and does not validate the file type and spaceName parameter.

## References
- https://github.com/xuhuisheng/lemon/issues/175
