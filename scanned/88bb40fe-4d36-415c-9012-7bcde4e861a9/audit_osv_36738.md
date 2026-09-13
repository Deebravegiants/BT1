# [C] InvoicePlane Vulnerable to Remote Code Execution via Local File Inclusion and Log Poisoning

## Summary
Severity: Critical
Advisory: CVE-2026-25548
Aliases: GHSA-g6rw-m9mf-33ch
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-25548
Type: osv

## Details
InvoicePlane is a self-hosted open source application for managing invoices, clients, and payments. A critical Remote Code Execution (RCE) vulnerability exists in InvoicePlane 1.7.0 through a chained Local File Inclusion (LFI) and Log Poisoning attack. An authenticated administrator can execute arbitrary system commands on the server by manipulating the `public_invoice_template` setting to include poisoned log files containing PHP code. Version 1.7.1 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25548.json
- https://github.com/InvoicePlane/InvoicePlane/security/advisories/GHSA-g6rw-m9mf-33ch
- https://nvd.nist.gov/vuln/detail/CVE-2026-25548
- https://github.com/InvoicePlane/InvoicePlane/commit/93622f2df88a860d89bfee56012cabb2942061d6
