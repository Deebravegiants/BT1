# [M] Invoice Ninja Denylist Bypass may Lead to Stored XSS via Invoice Line Items

## Summary
Severity: Medium
Advisory: GHSA-98wm-cxpw-847p
CVE: CVE-2026-33628
CWE: CWE-116, CWE-184, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-98wm-cxpw-847p
Type: github-advisory

## Affected
- Packagist: `invoiceninja/invoiceninja` — affected >=0 <5.13.4

## Details
## Vulnerability Details

Invoice line item descriptions in Invoice Ninja v5.13.0 bypass the XSS denylist filter, allowing stored XSS payloads to execute when invoices are rendered in the PDF preview or client portal.

The line item description field was not passed through `purify::clean()` before rendering.

## Steps to Reproduce

1. Login as any authenticated user
2. Create or edit an invoice
3. In a line item description, enter: `<img src=x onerror=alert(document.cookie)>`
4. Save the invoice and preview it
5. The XSS payload executes in the browser

## Impact

- **Attacker**: Any authenticated user who can create invoices
- **Victim**: Any user viewing the invoice (including clients via the portal)
- **Specific damage**: Session hijacking, account takeover, data exfiltration

## Proposed Fix

Fixed in v5.13.4 by the vendor by adding `purify::clean()` to sanitize line item descriptions.

## References
- https://github.com/invoiceninja/invoiceninja/security/advisories/GHSA-98wm-cxpw-847p
- https://nvd.nist.gov/vuln/detail/CVE-2026-33628
- https://github.com/invoiceninja/invoiceninja/commit/b81a3fc302573fc4a53d61e8537dd19154ce1091
- https://github.com/invoiceninja/invoiceninja
- https://github.com/invoiceninja/invoiceninja/releases/tag/v5.13.4
