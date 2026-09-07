# [H] Paymenter has URL parameter injection that bypasses paid plan limits at checkout

## Summary
Severity: High
Advisory: GHSA-5q4q-834j-g8g4
CVE: CVE-2026-47198
CWE: CWE-20, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-5q4q-834j-g8g4
Type: github-advisory

## Affected
- Packagist: `paymenter/paymenter` — affected >=0 <1.5.1

## Details
### Summary
The checkout component improperly filters URL-writable properties, allowing authenticated users to inject arbitrary key-value pairs into server provisioning parameters. Because bundled server extensions prioritize these user-supplied properties over administrator-defined configurations, a regular user can override hosting plans and resource limits at checkout without special privileges.

### Technical Details
The `Checkout` Livewire component (`app/Livewire/Products/Checkout.php`) exposes the `$checkoutConfig` property to URL query parameters via the `#[Url]` attribute (aliased as `config`). 

When processing this input:
1. Validation rules are dynamically generated *only* for keys explicitly defined by an extension's `getCheckoutConfig()` method. Any undefined keys injected into the query parameter bypass validation entirely.
2. The cart component (`app/Livewire/Cart.php`) stores all keys from `checkout_config` directly into the database without sanitation:
```php
   foreach ($item->checkout_config as $key => $value) {
       $service->properties()->updateOrCreate(['key' => $key], ['value' => $value]);
   }
```
3. During server provisioning, app/Helpers/ExtensionHelper.php retrieves these stored properties and passes them to the extension's createServer() method.

Because of how individual server extensions handle these properties, user-injected data overrides intended administrator settings.

### Impact
This is a business logic flaw that allows remote, authenticated users to manipulate server provisioning parameters.

Depending on the active extension, this leads to unauthorized overrides of core resource limits (such as CPU, RAM, storage, or package tiers). No administrative privileges are required to exploit this vulnerability.

## References
- https://github.com/Paymenter/Paymenter/security/advisories/GHSA-5q4q-834j-g8g4
- https://github.com/Paymenter/Paymenter
