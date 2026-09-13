# [H] CVE-2024-6472

## Summary
Severity: High
Advisory: CVE-2024-6472
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-08-05
Source: https://osv.dev/vulnerability/CVE-2024-6472
Type: osv

## Details
Certificate Validation user interface in LibreOffice allows potential vulnerability.




Signed macros are scripts that have been digitally signed by the 
developer using a cryptographic signature. When a document with a signed
 macro is opened a warning is displayed by LibreOffice before the macro 
is executed.

Previously if verification failed the user could fail to understand the failure and choose to enable the macros anyway.


This issue affects LibreOffice: from 24.2 before 24.2.5.

## References
- https://www.libreoffice.org/about-us/security/advisories/CVE-2024-6472
