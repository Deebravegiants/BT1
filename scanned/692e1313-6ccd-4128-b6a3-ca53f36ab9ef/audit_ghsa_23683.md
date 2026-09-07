# [M] WooCommerce Incorrect Authorization

## Summary
Severity: Medium
Advisory: GHSA-wwh8-v3j3-gxfw
CVE: CVE-2020-29156
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-wwh8-v3j3-gxfw
Type: github-advisory

## Affected
- Packagist: `woocommerce/woocommerce` — affected >=0 <4.7.0

## Details
The WooCommerce plugin before 4.7.0 for WordPress allows remote attackers to view the status of arbitrary orders via the `order_id` parameter in a `fetch_order_status` action.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-29156
- https://github.com/Ko-kn3t/CVE-2020-29156
- https://github.com/woocommerce/woocommerce
- https://raw.githubusercontent.com/woocommerce/woocommerce/master/changelog.txt
