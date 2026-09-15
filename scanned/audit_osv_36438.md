# [M] InvoicePlane has Unauthenticated Path Traversal in Guest Controller

## Summary
Severity: Medium
Advisory: CVE-2026-23491
Aliases: GHSA-88gq-mv54-v3fc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-23491
Type: osv

## Details
InvoicePlane is a self-hosted open source application for managing invoices, clients, and payments. A path traversal vulnerability exists in the `get_file` method of the `Guest` module's `Get` controller in InvoicePlane up to and including through 1.6.3. The vulnerability allows unauthenticated attackers to read arbitrary files on the server by manipulating the input filename. This leads to the disclosure of sensitive information, including configuration files with database credentials. Version 1.6.4 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23491.json
- https://github.com/InvoicePlane/InvoicePlane/security/advisories/GHSA-88gq-mv54-v3fc
- https://nvd.nist.gov/vuln/detail/CVE-2026-23491
- https://github.com/InvoicePlane/InvoicePlane/commit/add8bb798dde621f886823065ef1841986543c69
