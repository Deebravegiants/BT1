# [M] Shopper: Missing per-action authorization on PaymentMethods, Currencies and Carriers admin tables

## Summary
Severity: Medium
Advisory: GHSA-fxqw-97cc-7g5c
CVE: CVE-2026-47745
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-fxqw-97cc-7g5c
Type: github-advisory

## Affected
- Packagist: `shopper/framework` — affected >=0 <2.8.0

## Details
## Impact

The admin tables for `PaymentMethods`, `Currencies` and `Carriers` exposed inline toggles and per-record actions (enable, disable, edit, delete) that were rendered for any authenticated panel user without checking the corresponding per-action permission. A low-privilege user could:

- Disable every payment method on the store, blocking checkout.
- Disable or alter the default currency, changing displayed prices and the exchange rate basis.
- Disable carriers, breaking shipping rate computation at checkout.

The impact is a full denial of checkout and pricing integrity loss, reachable by any authenticated user.

## Patches

Fixed in `v2.8.0`. Each toggle and per-record action now requires its matching permission (`edit_payment_methods`, `edit_currencies`, `edit_carriers`).

Upgrade via:

```bash
composer require shopper/admin:^2.8
```

## Workarounds

None. Upgrade to `v2.8.0`.

## References
- https://github.com/shopperlabs/shopper/security/advisories/GHSA-fxqw-97cc-7g5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-47745
- https://github.com/shopperlabs/shopper/pull/511
- https://github.com/shopperlabs/shopper
