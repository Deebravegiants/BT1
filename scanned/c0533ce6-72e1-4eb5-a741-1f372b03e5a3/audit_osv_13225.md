# [M] CVE-2018-18688

## Summary
Severity: Medium
Advisory: CVE-2018-18688
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-01-07
Source: https://osv.dev/vulnerability/CVE-2018-18688
Type: osv

## Details
The Portable Document Format (PDF) specification does not provide any information regarding the concrete procedure of how to validate signatures. Consequently, an Incremental Saving vulnerability exists in multiple products. When an attacker uses the Incremental Saving feature to add pages or annotations, Body Updates are displayed to the user without any action by the signature-validation logic. This affects Foxit Reader before 9.4 and PhantomPDF before 8.3.9 and 9.x before 9.4. It also affects LibreOffice, Master PDF Editor, Nitro Pro, Nitro Reader, Nuance Power PDF Standard, PDF Editor 6 Pro, PDFelement6 Pro, PDF Studio Viewer 2018, PDF Studio Pro, Perfect PDF 10 Premium, and Perfect PDF Reader.

## References
- https://www.foxitsoftware.com/support/security-bulletins.php
- https://www.pdfa.org/recently-identified-pdf-digital-signature-vulnerabilities/
- https://pdf-insecurity.org/signature/evaluation_2018.html
- https://pdf-insecurity.org/signature/signature.html
