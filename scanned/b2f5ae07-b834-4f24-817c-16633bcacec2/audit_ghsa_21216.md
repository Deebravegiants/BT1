# [M] WooCommerce WordPress plugin before 6.6.0 vulnerable to stored HTML injection

## Summary
Severity: Medium
Advisory: GHSA-jwvf-28fg-g4xg
CVE: CVE-2022-2099
CWE: CWE-116, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-18
Source: https://github.com/advisories/GHSA-jwvf-28fg-g4xg
Type: github-advisory

## Affected
- Packagist: `woocommerce/woocommerce` — affected >=0 <6.6.0

## Details
The WooCommerce WordPress plugin before 6.6.0 is vulnerable to stored HTML injection due to lack of escaping and sanitizing in the payment gateway titles

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2099
- https://github.com/woocommerce/woocommerce
- https://wpscan.com/vulnerability/0316e5f3-3302-40e3-8ff4-be3423a3be7b
