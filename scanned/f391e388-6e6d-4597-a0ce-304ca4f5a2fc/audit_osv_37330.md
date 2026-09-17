# [C] CVE-2026-31017

## Summary
Severity: Critical
Advisory: CVE-2026-31017
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-31017
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in the Print Format functionality of ERPNext v16.0.1 and Frappe Framework v16.1.1, where user-supplied HTML is insufficiently sanitized before being rendered into PDF. When generating PDFs from user-controlled HTML content, the application allows the inclusion of HTML elements such as <iframe> that reference external resources. The PDF rendering engine automatically fetches these resources on the server side. An attacker can abuse this behavior to force the server to make arbitrary HTTP requests to internal services, including cloud metadata endpoints, potentially leading to sensitive information disclosure.

## References
- https://github.com/PhDg1410/CVE/tree/main/CVE-2026-31017
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31017.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31017
