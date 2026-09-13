# [H] CVE-2018-18274

## Summary
Severity: High
Advisory: CVE-2018-18274
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-12
Source: https://osv.dev/vulnerability/CVE-2018-18274
Type: osv

## Details
A issue was found in pdfalto 0.2. There is a heap-based buffer overflow in the TextPage::addAttributsNode function in XmlAltoOutputDev.cc.

## References
- https://github.com/kermitt2/pdfalto/issues/33
- https://github.com/TeamSeri0us/pocs/tree/master/pdfalto
