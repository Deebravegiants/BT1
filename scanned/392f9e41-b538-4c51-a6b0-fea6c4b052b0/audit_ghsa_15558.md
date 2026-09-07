# [M] Filament has unvalidated ColorColumn and ColorEntry values that can be used for Cross-site Scripting

## Summary
Severity: Medium
Advisory: GHSA-9h9q-qhxg-89xr
CVE: CVE-2024-47186
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-27
Source: https://github.com/advisories/GHSA-9h9q-qhxg-89xr
Type: github-advisory

## Affected
- Packagist: `filament/tables` — affected >=3.0.0 <3.2.115
- Packagist: `filament/infolists` — affected >=3.0.0 <3.2.115

## Details
### Summary

If values passed to a `ColorColumn` or `ColumnEntry` are not valid and contain a specific set of characters, applications are vulnerable to XSS attack against a user who opens a page on which a color column or entry is rendered.

Versions of Filament from v3.0.0 through v3.2.114 are affected.

Please upgrade to Filament [v3.2.115](https://github.com/filamentphp/filament/releases/tag/v3.2.115).

### PoC

For example, using a value such as:

```html
blue;"><script>alert('There\'s a security problem here')</script style="
```

Would get passed into the `@style()` Blade directive from Laravel to render the correct background color, where `$state` contains the value:

```blade
<div @style([
    "background-color: {$state}" => $state,
])></div>
```

Since Laravel does not escape special characters within the `@style` Blade directive, the effective output HTML would be:

```html
<div style="background-color: blue;"><script>alert('There\'s a security problem here')</script style=""></div>
```

Creating the opportunity for arbitrary JS to run if it was stored in the database.

### Response

This vulnerability (in `ColorColumn` only) was reported by @sv-LayZ, who reported the issue and patched the issue during the evening of 25/09/2024. Thank you Mattis.

The review process concluded on 27/09/2024, which revealed the issue was also present in `ColorEntry`. This was fixed the same day and Filament [v3.2.115](https://github.com/filamentphp/filament/releases/tag/v3.2.115) followed to escape any special characters while outputting inline styles like this:

```blade
<div @style([
    'background-color: ' . e($state) => $state,
])></div>
```

Although these components are no longer vulnerable to this type of XSS attack, it is good practice to validate colors, and since many Filament users may be accepting color input using the `ColorPicker` form component, [additional color validation documentation was published](https://filamentphp.com/docs/3.x/forms/fields/color-picker#color-picker-validation).

## References
- https://github.com/filamentphp/filament/security/advisories/GHSA-9h9q-qhxg-89xr
- https://github.com/filamentphp/filament/commit/df7989352464d08eda5837ef50f9997fad902316
- https://github.com/filamentphp/filament
- https://github.com/filamentphp/filament/releases/tag/v3.2.115
