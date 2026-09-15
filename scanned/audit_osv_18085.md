# [H] CVE-2020-23872

## Summary
Severity: High
Advisory: CVE-2020-23872
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-10
Source: https://osv.dev/vulnerability/CVE-2020-23872
Type: osv

## Details
A NULL pointer dereference in the function TextPage::restoreState of pdf2xml v2.0 allows attackers to cause a denial of service (DoS).

## References
- https://github.com/Aurorainfinity/Poc/tree/master/pdf2xml
- https://github.com/kermitt2/pdf2xml/issues/10
