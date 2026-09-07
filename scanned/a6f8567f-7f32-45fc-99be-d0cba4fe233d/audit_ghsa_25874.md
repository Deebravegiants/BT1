# [M] Possibility for Denial of Service by overwriting PHP files with language exports

## Summary
Severity: Medium
Advisory: GHSA-3fvf-2gp4-89wq
Ecosystem: Packagist
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-3fvf-2gp4-89wq
Type: github-advisory

## Affected
- Packagist: `barryvdh/laravel-translation-manager` — affected >=0 <0.6.2

## Details
### Impact
Laravel Translation Manager didn't check the locale name, which allowed directory traversal when exporting files. The content would be a PHP file returning an array of translations, but this could lead to unexpected results, like denial of service. Access to the Laravel Translation Manager is required, because a new locale would have to be added and published.

### Patches
Version 0.6.2 fixes this issue.

### Workarounds
Only allow trusted admins to publish/edit translations.

### References
https://github.com/barryvdh/laravel-translation-manager/pull/417

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/barryvdh/laravel-translation-manager
* Email me (see Github profile)

### Credits
Found and reported by [Natalia Trojanowska](https://www.linkedin.com/in/trojanowskanatalia/)

## References
- https://github.com/barryvdh/laravel-translation-manager/security/advisories/GHSA-3fvf-2gp4-89wq
- https://github.com/barryvdh/laravel-translation-manager
