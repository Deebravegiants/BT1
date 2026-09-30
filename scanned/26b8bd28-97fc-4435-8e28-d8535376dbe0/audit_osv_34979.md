# [M] CVE-2025-67082

## Summary
Severity: Medium
Advisory: CVE-2025-67082
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2025-67082
Type: osv

## Details
An SQL injection vulnerability in InvoicePlane through 1.6.3 has been identified in "maxQuantity" and "minQuantity" parameters when generating a report. An authenticated attacker can exploit this issue via error-based SQL injection, allowing for the extraction of arbitrary data from the database. The vulnerability arises from insufficient sanitizing of single quotes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67082.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67082
- https://www.helx.io/blog/advisory-invoice-plane/
- https://github.com/InvoicePlane/InvoicePlane
