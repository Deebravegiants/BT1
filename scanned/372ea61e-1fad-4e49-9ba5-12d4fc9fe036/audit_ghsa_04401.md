# [H] Shopper: Multiple data integrity and disclosure issues in admin Livewire components

## Summary
Severity: High
Advisory: GHSA-hr9v-r8r2-hg7j
CVE: CVE-2026-47743
CWE: CWE-200, CWE-639, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-hr9v-r8r2-hg7j
Type: github-advisory

## Affected
- Packagist: `shopper/framework` — affected >=0 <2.8.0

## Details
## Impact

Three related defects on admin Livewire components allowed data tampering, sensitive data disclosure, and stored XSS:

- **IDOR via unlocked properties.** Several Livewire components in the admin panel exposed Eloquent model identifiers as public properties without the `#[Locked]` attribute. An authenticated user could rewrite the wire payload from the browser to target any record id, bypassing the implicit scoping enforced by the page routing.
- **Sensitive data echoed back through Hidden form field.** `Customers/Create::store()` re-passed a `Hidden` `_password` form field straight into the create payload. The plaintext password was rendered into the HTML and transported through the Livewire snapshot in clear text, exposing credentials in the page DOM and in any logging that captures Livewire payloads.
- **Stored XSS on product barcode.** The product barcode field was rendered through `DNS1DFacade::getBarcodeHTML()` with `{!! !!}`. An attacker with `edit_products` permission could persist malicious payload in the barcode field that would execute in the browser of any admin user viewing that product, enabling session theft and privileged-action chaining.

## Patches

Fixed in `v2.8.0`:

- All vulnerable Livewire model identifiers are now marked `#[Locked]`.
- `Customers/Create` no longer round-trips the password through a Hidden form field; the plaintext password is hashed at action boundary and never returned to the client.
- The product barcode rendering now escapes the value before passing it to the barcode generator and the output is wrapped in an `<svg>` context that does not interpret event handlers.

Upgrade via:

```bash
composer require shopper/admin:^2.8
```

## Workarounds

None. Upgrade to `v2.8.0`.

## References
- https://github.com/shopperlabs/shopper/security/advisories/GHSA-hr9v-r8r2-hg7j
- https://github.com/shopperlabs/shopper/pull/511
- https://github.com/shopperlabs/shopper
