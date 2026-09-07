# [H] Craft CMS Vulnerable to potential authenticated Remote Code Execution via malicious attached Behavior

## Summary
Severity: High
Advisory: GHSA-7jx7-3846-m7w7
CVE: CVE-2026-25498
CWE: CWE-470
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-09
Source: https://github.com/advisories/GHSA-7jx7-3846-m7w7
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.22
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.16.18

## Details
## Relationship to Previously Patched Vulnerability

This vulnerability is **in addition to** the RCE vulnerability patched in [GHSA-255j-qw47-wjh5](https://github.com/craftcms/cms/security/advisories/GHSA-255j-qw47-wjh5). That advisory addressed a similar RCE vulnerability that affected two specific routes:

- `/index.php?p=admin%2Factions%2Ffields%2Fapply-layout-element-settings`
- `/index.php?p=admin%2Factions%2Ffields%2Frender-card-preview`

This one addresses some additional endpoints that were not covered in the https://github.com/craftcms/cms/security/advisories/GHSA-255j-qw47-wjh5.

The patched vulnerability used a malicious `AttributeTypecastBehavior` with a wildcard event listener (`"on *": "self::beforeSave"`) and `__construct()` syntax to trigger RCE via the `typecastBeforeSave` callback. The fix was implemented in commits:
- [6e608a1](https://github.com/craftcms/cms/commit/6e608a1a5bfb36943f94f584b7548ca542a86fef)
- [27f5588](https://github.com/craftcms/cms/commit/27f55886098b56c00ddc53b69239c9c9192252c7)
- [ec43c49](https://github.com/craftcms/cms/commit/ec43c497edde0b2bf2e39a119cded2e55f9fe593)

This vulnerability follows the same attack pattern (behavior injection via `"as <behavior>"` syntax) but affects a **different code path** (`assembleLayoutFromPost()` in `Fields.php`) that was **not patched** in those commits. The attack vector uses `typecastAfterValidate` instead of `typecastBeforeSave` and does not require the wildcard event listener syntax, demonstrating that multiple entry points exist for this type of vulnerability.

---

## Executive Summary

A Remote Code Execution (RCE) vulnerability exists in Craft CMS where the `assembleLayoutFromPost()` function in `src/services/Fields.php` fails to sanitize user-supplied configuration data before passing it to `Craft::createObject()`. This allows authenticated administrators to inject malicious Yii2 behavior configurations that execute arbitrary system commands on the server. This vulnerability represents an **unpatched variant** of the behavior injection vulnerability addressed in GHSA-255j-qw47-wjh5, affecting different endpoints through a separate code path.

---

## Vulnerability Details

### Attack Prerequisites

- **Authentication:** Admin-level access required
- **Network Access:** Access to admin panel (`/admin`)

---


### Location

- **File:** `src/services/Fields.php`
- **Function:** `assembleLayoutFromPost()` (lines 1125-1143)
- **Root Cause:** Missing `cleanseConfig()` call on user-supplied `fieldLayout` POST parameter

### Vulnerable Code Path

```php
// src/services/Fields.php:1125-1133
public function assembleLayoutFromPost(?string $namespace = null): FieldLayout
{
    $paramPrefix = $namespace ? rtrim($namespace, '.') . '.' : '';
    $request = Craft::$app->getRequest();
    $config = JsonHelper::decode($request->getBodyParam("{$paramPrefix}fieldLayout"));
    // ... additional config values added ...
    $layout = $this->createLayout($config);  // <-- No cleanseConfig() call!
    // ...
}

// src/services/Fields.php:1089-1093
public function createLayout(array $config): FieldLayout
{
    $config['class'] = FieldLayout::class;
    return Craft::createObject($config);  // <-- Untrusted data passed directly
}
```
---

## Attack Chain

The exploitation leverages Yii2's object configuration system and behavior attachment mechanism:

1. **Behavior Injection:** Attacker includes `'as rce'` key in the `fieldLayout` JSON POST parameter
2. **Object Creation:** `Craft::createObject()` processes the config through Yii2's `BaseYii::configure()`
3. **Behavior Attachment:** Yii2's `Component::__set()` detects the `'as '` prefix and attaches the behavior
4. **RCE Trigger:** When `validate()` is called on the model, `EVENT_AFTER_VALIDATE` fires
5. **Command Execution:** `AttributeTypecastBehavior` calls the configured typecast function (`ConsoleProcessus::execute`) with the `uid` attribute value as the command

### RCE Gadget Chain

```
FieldLayout POST parameter
    → Craft::createObject()
    → Yii2 Component::__set() with 'as rce' key
    → AttributeTypecastBehavior attached
    → Model::validate() called
    → EVENT_AFTER_VALIDATE triggered
    → typecastAfterValidate → typecastAttributes()
    → call_user_func(['Psy\Readline\Hoa\ConsoleProcessus', 'execute'], $command)
    → Shell command execution
```

---

## Affected Controllers

The `assembleLayoutFromPost()` function is called by multiple admin controllers:

| Controller | Action | Permission Required |
|------------|--------|---------------------|
| `TagsController` | `actionSaveTagGroup()` | Admin |
| `CategoriesController` | `actionSaveGroup()` | Admin |
| `EntryTypesController` | `actionSave()` | Admin |
| `GlobalsController` | `actionSaveSet()` | Admin |
| `VolumesController` | `actionSave()` | Admin |
| `UsersController` | `actionSaveUserFieldLayout()` | Admin |
| `AddressesController` | `actionSaveAddressFieldLayout()` | Admin |

---
## References

- https://github.com/craftcms/cms/commit/395c64f0b80b507be1c862a2ec942eaacb353748
- [GHSA-255j-qw47-wjh5](https://github.com/craftcms/cms/security/advisories/GHSA-255j-qw47-wjh5) - Previously patched RCE vulnerability via behavior injection (affecting different endpoints)
- [CVE-2024-4990](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2024-4990) - Related vulnerability that inspired the behavior injection attack pattern
- [Yii2 GHSA-gcmh-9pjj-7fp4](https://github.com/yiisoft/yii2/security/advisories/GHSA-gcmh-9pjj-7fp4) - Original Yii framework report (framework team declined to fix at framework level)

---

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-7jx7-3846-m7w7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25498
- https://github.com/craftcms/cms/commit/395c64f0b80b507be1c862a2ec942eaacb353748
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.16.18
- https://github.com/craftcms/cms/releases/tag/5.8.22
