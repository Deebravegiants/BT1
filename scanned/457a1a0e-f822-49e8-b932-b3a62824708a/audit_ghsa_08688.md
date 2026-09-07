# [H] Pimcore Admin Classic Bundle Vulnerable to SQL Injection in Translation Grid Date Filter via Unsanitized Property Parameter

## Summary
Severity: High
Advisory: GHSA-h4ph-crvj-9h92
CVE: CVE-2026-44741
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-h4ph-crvj-9h92
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=2.0.0-RC1 <2.3.6
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.7.18

## Details
# GitHub Security Advisory Draft — GM-369

## Summary
SQL injection in Pimcore's translation grid date filter — the user-supplied `property` field from the filter JSON is interpolated directly into a `UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(...)))` SQL expression without parameterization or allowlist validation.

## Severity
CVSS 3.1: 8.8 (High) — AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H

## Affected Component
- **Package:** `pimcore/admin-ui-classic-bundle`
- **File:** `src/Controller/Admin/TranslationController.php`
- **Lines:** 565 (input), 569 (inadequate sanitization), 593 (injection point)
- **Endpoint:** `POST /admin/translation/translations`

## Description
The translation grid endpoint processes JSON filter parameters. When a filter has `type: "date"`, the `property` field is extracted and used to construct a SQL expression:

```php
$fieldname = $filter[$propertyField];              // Line 565 — user input
$fieldname = str_replace('--', '', $fieldname);    // Line 569 — trivially bypassable
$fieldname = $tableName . '.' . $fieldname;        // Line 577
$fieldname = "UNIX_TIMESTAMP(DATE(FROM_UNIXTIME({$fieldname})))";  // Line 593 — injection
```

The `str_replace('--', '')` sanitization is trivially bypassable (use `/**/` comments or `----`). In non-language mode, `$fieldname` is concatenated directly into the SQL condition without quoting or parameterization.

## Impact
Authenticated user with translations view permission can extract arbitrary database data via UNION-based or error-based SQL injection. Combined with GM-249 (unsafe unserialize), this enables an SQLi → deserialization → RCE chain.

## Proof of Concept
```
POST /admin/translation/translations
filter=[{"property":"1))) UNION SELECT password FROM users WHERE ((1","type":"date","operator":"eq","value":"2026-01-01"}]
```

## Suggested Fix
Validate `$fieldname` against an allowlist of valid column names before SQL interpolation:
```php
$allowedDateColumns = ['creationDate', 'modificationDate'];
if (!in_array($fieldname, $allowedDateColumns, true)) {
    continue;
}
```

## References
- CWE-89: SQL Injection
- Related: CVE-2026-27461 (RLIKE injection in Dependency/Dao.php — different code path)


---

## Suggested Fix

In `TranslationController.php`: (1) Add allowlist check for non-language fieldnames before processing. (2) Replace raw string interpolation `UNIX_TIMESTAMP(DATE(FROM_UNIXTIME({$fieldname})))` with `$db->quoteIdentifier($fieldname)` to prevent SQL injection in date filter expressions.

```diff
--- a/src/Controller/Admin/TranslationController.php
+++ b/src/Controller/Admin/TranslationController.php
@@ -569,7 +569,15 @@ class TranslationController extends AdminAbstractController
                 $fieldname = str_replace('--', '', $fieldname);
 
                 if (!$languageMode && in_array($fieldname, $validLanguages)
                     || $languageMode && !in_array($fieldname, $validLanguages)) {
                     continue;
                 }
 
+                // Allowlist non-language fieldnames to prevent SQL injection
+                $allowedNonLanguageFields = ['key', 'type', 'creationDate', 'modificationDate'];
+                if (!$languageMode && !in_array($fieldname, $allowedNonLanguageFields) && !in_array($fieldname, $validLanguages)) {
+                    continue;
+                }
+
                 if (!$languageMode) {
                     $fieldname = $tableName . '.' . $fieldname;
                 }
@@ -582,7 +590,7 @@ class TranslationController extends AdminAbstractController
                         } elseif ($filter[$operatorField] == 'eq') {
                             $operator = '=';
-                            $fieldname = "UNIX_TIMESTAMP(DATE(FROM_UNIXTIME({$fieldname})))";
+                            // Use validated fieldname only — never interpolate raw user input into SQL functions
+                            $fieldname = sprintf('UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(%s)))', $db->quoteIdentifier($fieldname));
                         }

```

---

## Proposed Fix

```diff
--- a/src/Controller/Admin/TranslationController.php
+++ b/src/Controller/Admin/TranslationController.php
@@ -569,7 +569,15 @@ class TranslationController extends AdminAbstractController
                 $fieldname = str_replace('--', '', $fieldname);
 
                 if (!$languageMode && in_array($fieldname, $validLanguages)
                     || $languageMode && !in_array($fieldname, $validLanguages)) {
                     continue;
                 }
 
+                // Allowlist non-language fieldnames to prevent SQL injection
+                $allowedNonLanguageFields = ['key', 'type', 'creationDate', 'modificationDate'];
+                if (!$languageMode && !in_array($fieldname, $allowedNonLanguageFields) && !in_array($fieldname, $validLanguages)) {
+                    continue;
+                }
+
                 if (!$languageMode) {
                     $fieldname = $tableName . '.' . $fieldname;
                 }
@@ -582,7 +590,7 @@ class TranslationController extends AdminAbstractController
                         } elseif ($filter[$operatorField] == 'eq') {
                             $operator = '=';
-                            $fieldname = "UNIX_TIMESTAMP(DATE(FROM_UNIXTIME({$fieldname})))";
+                            // Use validated fieldname only — never interpolate raw user input into SQL functions
+                            $fieldname = sprintf('UNIX_TIMESTAMP(DATE(FROM_UNIXTIME(%s)))', $db->quoteIdentifier($fieldname));
                         }
```

Happy to submit this as a PR against a private fork if that is the preferred workflow.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-h4ph-crvj-9h92
- https://github.com/pimcore/admin-ui-classic-bundle/pull/1111
- https://github.com/pimcore/admin-ui-classic-bundle/commit/80e57a23d9e19574eddfe9b08e8f26785b2b0d90
- https://github.com/pimcore/admin-ui-classic-bundle/releases/tag/v2.3.6
- https://github.com/pimcore/pimcore
