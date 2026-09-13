# [M] Shopware Customer Orders can be canceled, even if refunds are disabled

## Summary
Severity: Medium
Advisory: GHSA-r2vg-hvjm-fg38
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-r2vg-hvjm-fg38
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.3.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.7
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.3.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.7

## Details
Refunds in general can be enabled through the administration setting `core.cart.enableOrderRefunds` (in the cart panel).Which visually shows and hides the button. However, using a custom crafted request, a customer can still cancel his own orders.As this is not checked inside the route (and also not in the controller):
https://github.com/shopware/shopware/blob/trunk/src/Storefront/Controller/AccountOrderController.php#L98
https://github.com/shopware/shopware/blob/trunk/src/Core/Checkout/Order/SalesChannel/CancelOrderRoute.php

To mitigate this, a check should be added to the `CancelOrderRoute` which verifies that the feature is enabled.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-r2vg-hvjm-fg38
- https://github.com/shopware/shopware/commit/b157508aef2c820e7ff89ebd5848d3019f22b592
- https://github.com/shopware/shopware
