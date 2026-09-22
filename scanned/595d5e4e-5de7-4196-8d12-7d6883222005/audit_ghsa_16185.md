# [C] Deserialization of Untrusted Data in dompdf/dompdf

## Summary
Severity: Critical
Advisory: GHSA-577p-7j7h-2jgf
CVE: CVE-2021-3838
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-577p-7j7h-2jgf
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <2.0.0

## Details
DomPDF before version 2.0.0 is vulnerable to PHAR (PHP Archive) deserialization due to a lack of checking on the protocol before passing it into the file_get_contents() function. An attacker who can upload files of any type to the server can pass in the phar:// protocol to unserialize the uploaded file and instantiate arbitrary PHP objects. This can lead to remote code execution, especially when DOMPdf is used with frameworks with documented POP chains like Laravel or vulnerable developer code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3838
- https://github.com/dompdf/dompdf/commit/99aeec1efec9213e87098d42eb09439e7ee0bb6a
- https://github.com/dompdf/dompdf
- https://huntr.com/bounties/0bdddc12-ff67-4815-ab9f-6011a974f48e
