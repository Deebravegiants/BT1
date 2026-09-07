# [M] Shopware vulnerable to MediaVisibilityRestrictionSubscriber bypass when reading media entities by aggregating fields individually

## Summary
Severity: Medium
Advisory: GHSA-m895-2hj3-8cg9
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-m895-2hj3-8cg9
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.3.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.7
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.3.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.7

## Details
In Shopware core and platform versions before 6.6.10.7 and 6.7.3.1, media visibility restrictions applied by MediaVisibilityRestrictionSubscriber are not enforced for aggregation API requests. Authorization filters are only injected during standard entity reads; aggregation queries can be constructed to bypass these checks and enumerate private media records such as invoices or other restricted documents. A low‑privilege backend user (e.g., product editor) can chain normal business flows (creating or viewing orders) with aggregation queries to disclose sensitive customer data including addresses and payment-related information contained within associated private media. The issue is resolved in 6.6.10.7 and 6.7.3.1.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-m895-2hj3-8cg9
- https://github.com/shopware/shopware/commit/0965b35a527756faab2cec5a4ff172d79b0f99be
- https://github.com/shopware/shopware
