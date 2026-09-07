# [H] Payment information sent to PayPal not necessarily identical to created order

## Summary
Severity: High
Advisory: GHSA-vxpm-8hcp-qh27
CVE: CVE-2023-23941
CWE: CWE-345
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-02-03
Source: https://github.com/advisories/GHSA-vxpm-8hcp-qh27
Type: github-advisory

## Affected
- Packagist: `swag/paypal` — affected >=0 <5.4.4

## Details
### Impact
If JavaScript-based PayPal checkout methods are used (PayPal Plus, Smart Payment Buttons, SEPA, Pay Later, Venmo, Credit card), the amount and item list sent to PayPal may not be identical to the one in the created order.

### Patches
The problem has been fixed with version 5.4.4

### Workarounds
Disable the aforementioned payment methods or use the Security Plugin in version >= 1.0.21.

### References
[Shopware blog post](https://news.shopware.com/security-issue-in-paypal-plugin-update-required)

## References
- https://github.com/shopware/SwagPayPal/security/advisories/GHSA-vxpm-8hcp-qh27
- https://nvd.nist.gov/vuln/detail/CVE-2023-23941
- https://github.com/shopware/SwagPayPal/commit/57db5f4a57ef0a1646b509b415de9f03bf441b08
- https://github.com/shopware/SwagPayPal
