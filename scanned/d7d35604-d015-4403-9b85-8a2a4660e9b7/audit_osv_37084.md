# [H] Initiative Vulnerable to Token Theft via Stored XSS in Document Uploads

## Summary
Severity: High
Advisory: CVE-2026-28274
Aliases: GHSA-v38c-x27x-p584
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-28274
Type: osv

## Details
Initiative is a self-hosted project management platform. Versions of the application prior to 0.32.4 are vulnerable to Stored Cross-Site Scripting (XSS) in the document upload functionality. Any user with upload permissions within the "Initiatives" section can upload a malicious `.html` or `.htm` file as a document. Because the uploaded HTML file is served under the application's origin without proper sandboxing, the embedded JavaScript executes in the context of the application. As a result, authentication tokens, session cookies, or other sensitive data can be exfiltrated to an attacker-controlled server. Additionally, since the uploaded file is hosted under the application's domain, simply sharing the direct file link may result in execution of the malicious script when accessed. Version 0.32.4 fixes the issue.

## References
- https://github.com/Morelitea/initiative/releases/tag/v0.32.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28274.json
- https://github.com/Morelitea/initiative/security/advisories/GHSA-v38c-x27x-p584
- https://nvd.nist.gov/vuln/detail/CVE-2026-28274
