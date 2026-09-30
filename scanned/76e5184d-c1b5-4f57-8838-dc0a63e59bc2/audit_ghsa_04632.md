# [M] Shopware: Admin Account Takeover via User Recovery Hash Exposure

## Summary
Severity: Medium
Advisory: GHSA-8v9p-g828-v98f
CVE: CVE-2026-48009
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-8v9p-g828-v98f
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.18
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.18

## Details
## Summary

A low-privilege admin user with `user_recovery:read` ACL can take over any admin account. The attacker triggers password recovery for the victim (unauthenticated endpoint), reads the recovery hash from the Admin API search endpoint, then uses the hash to reset the victim's password (another unauthenticated endpoint). The recovery hash — intended to be secret and delivered only via email — is fully readable through the standard entity search API.

**OWASP:** A01:2021 — Broken Access Control

## Root Cause

The `user_recovery` entity exposes its `hash` field through the Admin API search endpoint (`POST /api/search/user-recovery`). The `hash` field lacks `ApiAware(false)` or `ReadProtection`, so any user with `user_recovery:read` ACL can read it.

The password recovery flow assumes the hash is delivered exclusively via email. The Admin API provides an alternative channel to obtain it, breaking this assumption.

**Three endpoints combine to form the attack:**

1. `POST /api/_action/user/user-recovery` — triggers recovery, creates hash in DB (**no auth required**)
2. `POST /api/search/user-recovery` — reads the hash (**requires only `user_recovery:read` ACL**)
3. `PATCH /api/_action/user/user-recovery/password` — resets password using hash (**no auth required**)

**Vulnerable code:**
- `src/Core/System/User/Recovery/UserRecoveryDefinition.php` — `hash` field is `ApiAware` with no `ReadProtection`

## Impact

- **Full admin account takeover** — attacker gains the highest privilege level in the system
- **All admin capabilities** — user/role management, system configuration, plugin management, customer data access
- **Cascading compromise** — taken-over admin account can be used to pivot to other attacks
- **Low barrier** — `user_recovery:read` is a seemingly harmless permission that grants devastating access

## Remediation

Remove the `hash` field from API responses:

```php
// src/Core/System/User/Recovery/UserRecoveryDefinition.php
(new StringField('hash', 'hash'))
    ->addFlags(new Required(), new ApiAware(false)),
```

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-8v9p-g828-v98f
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.6.10.18
- https://github.com/shopware/shopware/releases/tag/v6.7.10.1
