# [H] CVE-2021-30472

## Summary
Severity: High
Advisory: CVE-2021-30472
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-05-26
Source: https://osv.dev/vulnerability/CVE-2021-30472
Type: osv

## Details
A flaw was found in PoDoFo 0.9.7. A stack-based buffer overflow in PdfEncryptMD5Base::ComputeOwnerKey function in PdfEncrypt.cpp is possible because of a improper check of the keyLength value.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1947458
