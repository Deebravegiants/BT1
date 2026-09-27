# [M] Shopware: Privilege Escalation via Sync API Integration Admin Flag Bypass

## Summary
Severity: Medium
Advisory: GHSA-gv8p-48fr-4fxg
CVE: CVE-2026-48008
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-gv8p-48fr-4fxg
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.18
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.10.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.18

## Details
## Summary

A non-admin API user with `integration:create` ACL privilege can escalate to full administrator by creating an integration with `admin: true` through the Sync API (`POST /api/_action/sync`). The regular integration endpoint (`POST /api/integration`) correctly blocks this, but the Sync API bypasses the controller-level check by writing directly through the DAL EntityWriter. The `integration` entity definition lacks `WriteProtection`, and the `admin` field has no field-level restriction flag.

**OWASP:** A01:2021 — Broken Access Control

## Root Cause

`IntegrationController::upsertIntegration()` checks `$source->isAdmin()` before allowing the `admin` field to be set. However, `SyncController::sync()` routes writes through `SyncService → EntityWriter`, which only applies:

1. `AclWriteValidator` — checks entity-level ACL (`integration:create` is sufficient)
2. `EntityProtectionValidator` — checks `WriteProtection` on entity definitions, but `IntegrationDefinition` has none

The `admin` field in `IntegrationDefinition` is a plain `BoolField` with no `WriteProtection` or special flag. The Sync API writes it without restriction.

**Vulnerable code path:**
- `src/Core/Framework/Api/Controller/SyncController.php` → `SyncService` → `EntityWriter::upsert()`
- **Missing protection:** `src/Core/Framework/Integration/IntegrationDefinition.php` — `admin` field has no `WriteProtection(Context::SYSTEM_SCOPE)`

**Working protection (bypassed):**
- `src/Core/Framework/Integration/IntegrationController.php:46-56` — `isAdmin()` check only applies to the dedicated controller endpoint

## Impact

- **Complete admin API access** — the escalated integration has full read/write on every entity: users, customers, orders, system configuration, integrations, plugins
- **PII exfiltration** — read all customer records (names, emails, addresses, order history)
- **Persistent backdoor** — the admin integration survives password changes and user deactivation

## Remediation

Add `WriteProtection(Context::SYSTEM_SCOPE)` to `IntegrationDefinition`, matching how `UserDefinition` and `AclRoleDefinition` are already protected:

```php
// src/Core/Framework/Integration/IntegrationDefinition.php
(new BoolField('admin', 'admin'))
    ->addFlags(new WriteProtection(Context::SYSTEM_SCOPE)),
```

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-gv8p-48fr-4fxg
- https://github.com/shopware/shopware
- https://github.com/shopware/shopware/releases/tag/v6.6.10.18
- https://github.com/shopware/shopware/releases/tag/v6.7.10.1
