# [M] Stirling-PDF Server-Side Request Forgery (SSRF)-Induced Arbitrary File Read Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-46568
Aliases: GHSA-998c-x8hx-737r
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2025-46568
Type: osv

## Details
Stirling-PDF is a locally hosted web application that allows you to perform various operations on PDF files. Prior to version 0.45.0, Stirling-PDF is vulnerable to SSRF-induced arbitrary file read. WeasyPrint redefines a set of HTML tags, including img, embed, object, and others. The references to several files inside, allow the attachment of content from any webpage or local file to a PDF. This allows the attacker to read any file on the server, including sensitive files and configuration files. All users utilizing this feature will be affected. This issue has been patched in version 0.45.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46568.json
- https://github.com/Stirling-Tools/Stirling-PDF/security/advisories/GHSA-998c-x8hx-737r
- https://nvd.nist.gov/vuln/detail/CVE-2025-46568
- https://github.com/Stirling-Tools/Stirling-PDF/commit/e15128633718cb5f9262986b3770ca592af60cda
