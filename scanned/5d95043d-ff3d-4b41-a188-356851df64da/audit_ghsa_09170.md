# [H] Pimcore has Unsafe PHP Deserialization in Multiple Locations Without allowed_classes Restriction

## Summary
Severity: High
Advisory: GHSA-36fc-7wjg-mfvj
CVE: CVE-2026-45162
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-36fc-7wjg-mfvj
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1 <12.3.7
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.17
- Packagist: `pimcore/pimcore` — affected >=2026.1.0 <2026.1.3

## Details
# GitHub Security Advisory Draft — GM-374

## Summary
Multiple locations in Pimcore v11 call PHP's `unserialize()` on data from database columns and filesystem files without the `allowed_classes` restriction, enabling object injection if an attacker can control the serialized data source.

## Severity
CVSS 3.1: 8.0 (High) — AV:N/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H

## Affected Component
- **Package:** `pimcore/pimcore` and `pimcore/admin-ui-classic-bundle`
- **Files:**
  - `lib/Tool/Authentication.php` (line 82) — session token deserialization
  - `models/Site/Dao.php` (line 68) — site domains from database
  - `models/DataObject/ClassDefinition/CustomLayout/Dao.php` (line 69) — layout definitions from database
  - `models/Tool/TmpStore/Dao.php` (line 64) — temporary store data from database
  - `models/Asset/WebDAV/Service.php` (line 36) — delete log from filesystem
  - `admin-ui-classic-bundle/src/Helper/Dashboard.php` (line 64) — dashboard config from filesystem

## Description
Six locations in Pimcore core call `unserialize()` directly (bypassing `Tool\Serialize`) on data sourced from database columns or filesystem files without passing the `allowed_classes` parameter. This means any class available in the autoloader will be instantiated during deserialization.

If an attacker can write to the data source (e.g., via SQL injection targeting the `tmp_store`, `sites`, or `custom_layouts` tables, or via a file write vulnerability targeting the WebDAV delete log), they can inject serialized PHP gadget chains that execute arbitrary code when the data is deserialized.

This is related to but distinct from the `Tool\Serialize::unserialize()` issue — these calls bypass the wrapper entirely.

## Impact
PHP object injection leading to Remote Code Execution when chained with a data source write vulnerability. Pimcore's dependency tree (Guzzle, Symfony, Monolog, Doctrine) provides numerous known gadget chains.

## Proof of Concept
1. Identify a writable data source (e.g., `tmp_store` table via SQL injection, or `webdav-delete.dat` via file write)
2. Write a serialized PHP gadget chain (e.g., Monolog `BufferHandler` chain from phpggc)
3. Trigger the deserialization (e.g., access a page that reads TmpStore, or trigger a WebDAV operation)
4. The gadget chain executes with web server privileges

## Suggested Fix
Add `allowed_classes` parameter to all `unserialize()` calls. Where no objects are needed, use `['allowed_classes' => false]`. Consider migrating to JSON serialization for data that doesn't require object preservation.

```php
// Example fix for Site/Dao.php:
$siteDomains = unserialize($site['domains'], ['allowed_classes' => false]);

// Example fix for TmpStore/Dao.php:
$item['data'] = unserialize($item['data'], ['allowed_classes' => false]);
```

## References
- CWE-502: Deserialization of Untrusted Data
- OWASP Deserialization Cheat Sheet
- phpggc: PHP Generic Gadget Chains

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-36fc-7wjg-mfvj
- https://github.com/pimcore/pimcore/pull/19119
- https://github.com/pimcore/pimcore/commit/4788bf3a3a7f2f760a8fe61e522565941e154e1e
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v12.3.7
