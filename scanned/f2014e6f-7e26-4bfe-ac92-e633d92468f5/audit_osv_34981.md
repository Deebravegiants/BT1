# [C] CVE-2025-67084

## Summary
Severity: Critical
Advisory: CVE-2025-67084
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2025-67084
Type: osv

## Details
File upload vulnerability in InvoicePlane through 1.6.3 allows authenticated attackers to upload arbitrary PHP files into attachments, which can later be executed remotely, leading to Remote Code Execution (RCE).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67084.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67084
- https://www.helx.io/blog/advisory-invoice-plane/
- https://github.com/InvoicePlane/InvoicePlane
