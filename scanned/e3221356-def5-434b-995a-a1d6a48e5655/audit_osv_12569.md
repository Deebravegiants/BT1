# [H] CVE-2018-12983

## Summary
Severity: High
Advisory: CVE-2018-12983
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-29
Source: https://osv.dev/vulnerability/CVE-2018-12983
Type: osv

## Details
A stack-based buffer over-read in the PdfEncryptMD5Base::ComputeEncryptionKey() function in PdfEncrypt.cpp in PoDoFo 0.9.6-rc1 could be leveraged by remote attackers to cause a denial-of-service via a crafted pdf file.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/LEJQUDZT4JRJSPZYY3UPSCTFPAC5TUHK/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UMEMSUUXA3SL3AZAKKCTZFXVPHTBBK3O/
- https://bugzilla.redhat.com/show_bug.cgi?id=1595693
