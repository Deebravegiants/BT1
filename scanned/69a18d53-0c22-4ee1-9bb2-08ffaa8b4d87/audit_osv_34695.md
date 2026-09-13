# [M] CVE-2025-64012

## Summary
Severity: Medium
Advisory: CVE-2025-64012
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-64012
Type: osv

## Details
InvoicePlane commit debb446c is vulnerable to Incorrect Access Control. The invoices/view handler fails to verify ownership before returning invoice data.

## References
- https://gist.github.com/tarekramm/797073e9ae991211ff2ae71ed1190c7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64012.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-64012
- https://github.com/InvoicePlane/InvoicePlane/commit/debb446ceaa84efc136987fc1e21b268f34e47b0
