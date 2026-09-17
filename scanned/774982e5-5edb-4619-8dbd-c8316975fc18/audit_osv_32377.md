# [M] CVE-2025-2866

## Summary
Severity: Medium
Advisory: CVE-2025-2866
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2025-04-27
Source: https://osv.dev/vulnerability/CVE-2025-2866
Type: osv

## Details
Improper Verification of Cryptographic Signature vulnerability in LibreOffice allows PDF Signature Spoofing by Improper Validation.




In the affected versions of LibreOffice a flaw in the verification code for adbe.pkcs7.sha1 signatures could cause invalid signatures to be accepted as valid




This issue affects LibreOffice: from 24.8 before < 24.8.6, from 25.2 before < 25.2.2.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00002.html
- https://www.libreoffice.org/about-us/security/advisories/cve-2025-2866
