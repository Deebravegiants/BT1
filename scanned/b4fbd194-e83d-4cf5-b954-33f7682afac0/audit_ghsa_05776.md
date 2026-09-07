# [M] Laravel Backpack CRUD: Stored XSS in the color column — the `@if($column['escaped'])` branches are inverted

## Summary
Severity: Medium
Advisory: GHSA-mmg4-322v-6jvc
CVE: CVE-2026-54181
CWE: CWE-1023, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-mmg4-322v-6jvc
Type: github-advisory

## Affected
- Packagist: `backpack/crud` — affected >=6.0.0 <6.8.14
- Packagist: `backpack/crud` — affected >=7.0.0 <7.0.38

## Details
## Summary

The Blade template for the `color` column type (`src/resources/views/crud/columns/color.blade.php`) has its escaped/unescaped rendering branches inverted relative to every other column template in the library. Because `$column['escaped']` defaults to `true`, values stored in color columns are rendered **unescaped by default**, enabling Stored XSS if column values are not validated before storage.

## Details

All other column templates in `src/resources/views/crud/columns/` follow the convention:
- `$column['escaped'] == true` → `{{ $column['text'] }}` (HTML-escaped)
- `$column['escaped'] == false` → `{!! $column['text'] !!}` (raw)

The `color` template has these branches swapped. An attacker who can write an arbitrary string to a `color`-typed column can inject JavaScript that executes in the browser of any user who views the list — including administrators — with access to their session cookies and CSRF tokens.

## Impact

Stored XSS with scope change (attacker context runs in victim's browser). Highest-risk target is an administrator viewing the list view. Exploitability requires the ability to write an unsanitized value into a `color`-typed column.

## Patches

Fixed in **6.8.14** and **7.0.38** by correcting the branch order in `color.blade.php`. See PR #5992.

## Workarounds

Validate stored color values against a strict CSS color grammar (e.g. `/^#[0-9a-fA-F]{3,6}$/`) at the model layer before data reaches the view.

## Credits

Reported by Vishal Shukla ([@shukla304](https://github.com/shukla304)) via sechub.dev.

## References
- https://github.com/Laravel-Backpack/CRUD/security/advisories/GHSA-mmg4-322v-6jvc
- https://github.com/Laravel-Backpack/CRUD
- https://github.com/Laravel-Backpack/CRUD/releases/tag/6.8.14
- https://github.com/Laravel-Backpack/CRUD/releases/tag/7.0.38
