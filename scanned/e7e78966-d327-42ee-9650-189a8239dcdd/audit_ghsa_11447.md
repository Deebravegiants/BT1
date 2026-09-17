# [H] Shopware: Unauthenticated data extraction possible through store-api.order endpoint

## Summary
Severity: High
Advisory: GHSA-7vvp-j573-5584
CVE: CVE-2026-31887
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-7vvp-j573-5584
Type: github-advisory

## Affected
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.8.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.15
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.8.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.15

## Details
### Summary

An insufficient check on the filter types for unauthenticated customers allows access to orders of other customers. This is part of the `deepLinkCode` support on the `store-api.order` endpoint.

### Details

#### Data Exposure

Depending on the order payload configuration, attackers may retrieve:
- Customer names
- Billing address
- Shipping address
- Email addresses
- Ordered products
- Order values
- Order numbers
- Order dates
- Payment method information
- Shipping method information
- More customs, depending on the given associations in the request

#### Security Impact

This vulnerability allows:
- Unauthorized access to foreign customer order data
- Mass enumeration of recent orders
- Potential scraping of customer personal information

#### Limitation

No limitation, but only orders from the past 30 days are checked for changeable means of payment (unrelated).

### Impact

The code is present since ~2021. Likely every version since then is impacted for every store.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-7vvp-j573-5584
- https://nvd.nist.gov/vuln/detail/CVE-2026-31887
- https://github.com/shopware/shopware
