# [M] Snipe-IT Vulnerable to User Account Escalation via CSV Import

## Summary
Severity: Medium
Advisory: GHSA-p68w-rgmg-3c2v
CVE: CVE-2026-49976
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-p68w-rgmg-3c2v
Type: github-advisory

## Affected
- Packagist: `snipe/snipe-it` — affected >=0 <8.6.0

## Details
### Impact
The CSV user import in update mode bypasses user-edit authorization. A user with only the `import` permission can overwrite any non-admin user's email by uploading a CSV, then trigger a password reset to take over the account.

`UserImporter.php` checks the `canEditAuthFields` gate and tries to strip auth fields from the model:

```php
// app/Importer/UserImporter.php:107-114
if (Auth::check() && (! Gate::allows('canEditAuthFields', $user))) {
    unset($user->username);
    unset($user->email);
    unset($user->password);
    unset($user->activated);
}
$user->update($this->sanitizeItemForUpdating($user));
```

The `unset()`s operate on the model, but `sanitizeItemForUpdating()` rebuilds its array from `$this->item` (the raw CSV row), not from the model:

```php
// app/Importer/ItemImporter.php:135-149
protected function sanitizeItemForStoring($model, $updating = false)
{
    $item = collect($this->item);                  // CSV data, not model attributes
    $item = $item->only($model->getFillable());
    if ($updating) {
        $item = $item->reject(fn($v) => empty($v));
    }
    return $item->toArray();
}
```

The attacker's CSV values pass through untouched.

For non-admin attacker vs. non-admin, non-superuser target, the gate returns `true` at `AuthServiceProvider.php:137`, so the `unset()` block never executes. The entire import path checks only `$this->authorize('import')` (`ImportController.php:196`); no `users.edit` check anywhere. The normal API route `PATCH /api/v1/users/{id}` correctly returns 403 for the same user. 

Attacker must have import privileges to exploit this, and that permission must be granted specifically and intentionally by a superadmin.


### Patches
Patched in v8.6.0

## References
- https://github.com/grokability/snipe-it/security/advisories/GHSA-p68w-rgmg-3c2v
- https://github.com/grokability/snipe-it
