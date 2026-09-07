# [H] Shopware vulnerable to a potential take over of app credentials

## Summary
Severity: High
Advisory: GHSA-c4p7-rwrg-pf6p
CVE: CVE-2026-31889
CWE: CWE-290
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-03-11
Source: https://github.com/advisories/GHSA-c4p7-rwrg-pf6p
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.8.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.15
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.8.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.15

## Details
### Summary

We identified and fixed a vulnerability in the Shopware app registration flow that could, under specific conditions, allow attackers to take over the communication channel between a shop and an app. By abusing app re‑registration, an attacker could redirect app traffic to an attacker‑controlled domain and potentially obtain API credentials intended for the legitimate shop.
We have no evidence that this vulnerability has been exploited.

---

### Affected Scope

- All apps (public and private) that use a `registrationUrl` in their app manifest and rely on the legacy HMAC‑based registration flow.
- Both on‑premise and cloud installations are affected until updated to a fixed Shopware version or protected by the latest Shopware Security Plugin.
- Shopware services and first‑party apps using the affected SDKs were reviewed and patched.
The vulnerability does not affect core storefront or administration authentication; it is limited to the app system’s registration and re‑registration mechanism.

---

### Impact

In a successful attack, an attacker who already knows certain app‑side secrets could:
- Re‑register an existing app installation with a domain under their control.
- Intercept App → Shop communication and cause data tampering (“data poisoning”).
- Obtain API integration credentials of the shop with the permissions granted to the app.
Shop owners and app manufacturers would typically observe this as “app malfunction” rather than an obvious security issue, which increases the need for hardening.

---

### Root Cause

The legacy app registration flow used HMAC‑based authentication without sufficiently binding a shop installation to its original domain. During re‑registration, the `shop-url` could be updated without proving control over the previously registered shop or domain. This made targeted hijacking of app communication feasible if an attacker possessed the relevant app‑side secret.

---

### Fix

We have hardened the app registration and re‑registration process:
- **Dual signature requirement:** Re‑registration now requires both the app secret and the existing shop secret to be presented and validated.
- **Mandatory secret rotation:** On successful re‑registration, a new shop secret is generated and verified; the previous secret is invalidated after a short grace period.
- **Stricter validation:** Shopware only accepts updated shop URLs and secrets once the full confirmation flow has completed successfully.
- **Improved logging and monitoring:** All re‑registrations are now logged with additional metadata to help detect abuse patterns.
These changes are delivered via:
- Updated Shopware core releases (6.6.x, 6.7.x), and
- Updated versions of the Shopware Security Plugin for supported older versions,
- Updated official SDKs (e.g. PHP and JavaScript app SDKs).
---

### Required Action

#### For Merchants / Shop Operators

1. **Update Shopware**
   - Upgrade to the latest Shopware 6.6.x / 6.7.x release that includes this fix, **or**
   - Install/update the latest Shopware Security Plugin version providing the hotfix for your Shopware 6 installation.
2. **Update apps**
   - Ensure all installed apps are updated to the latest versions provided by their manufacturers.
   - If you suspect compromised keys or observe unexpected app behaviour, re‑install the affected app or trigger key rotation as documented by the app vendor.

#### For App Manufacturers / Partners

1. **Update SDKs / implementations**
   - Update to the latest Shopware app SDKs (PHP / JS) or apply the documented changes if you maintain a custom implementation of the registration flow.
   - Validate **both** `shopware-app-signature` and `shopware-shop-signature` for re‑registration requests.
   - Always generate and store a new shop secret on re‑registration and only switch to it after a successful confirmation.
2. **Review your apps**
   - Verify that your app does not blindly accept changed `shop-url` values without validating signatures.
   - Check any logic that exposes data or functionality based solely on HMAC signatures from shops and ensure it aligns with the hardened registration model.
3. **Test your implementation**
   - Use the updated tooling and guidance provided in your Shopware Account / partner channels to validate that your registration flow complies with the new requirements.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-c4p7-rwrg-pf6p
- https://nvd.nist.gov/vuln/detail/CVE-2026-31889
- https://github.com/shopware/shopware
