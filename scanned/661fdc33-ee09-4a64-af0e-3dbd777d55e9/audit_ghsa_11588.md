# [M] Leantime has HTML injection through firstname and lastname fields

## Summary
Severity: Medium
Advisory: GHSA-qrfh-cc86-vc8c
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-qrfh-cc86-vc8c
Type: github-advisory

## Affected
- Packagist: `leantime/leantime` — affected >=0 <3.3.0

## Details
### Summary
Leantime v2.3.27 is vulnerable to Stored HTML Injection. The `firstname` and `lastname` fields in the admin user edit page are rendered without  HTML escaping, allowing an authenticated user to inject arbitrary HTML that executes when the profile is viewed.

### Vulnerable File
`app/Domain/Users/Templates/editUser.tpl.php`

### Vulnerable Code (Lines ~14-17)
```php
value="<?php echo $values['firstname'] ?>"
value="<?php echo $values['lastname'] ?>"
```
These fields output raw user input without sanitization.

### Steps to Reproduce
1. Login as admin > Go to Settings > Users > Edit any user
2. Enter HTML payload in First Name or Last Name field:
   `<h1>INJECTED</h1>`
3. Save the user profile
4. Create or view an article — the injected HTML renders in the author name

### Fix
Replace unescaped `echo` with `htmlspecialchars()`:
```php
value="<?php echo htmlspecialchars($values['firstname'], ENT_QUOTES, 'UTF-8') ?>"
value="<?php echo htmlspecialchars($values['lastname'], ENT_QUOTES, 'UTF-8') ?>"
```
Or use the existing `$this->e()` helper already used in `editOwn.tpl.php`.

### Impact
- Stored HTML injection visible to all users viewing affected content
- Can be used for phishing, fake login forms, and UI defacement
- Affects all versions before 3.3.0

## References
- https://github.com/Leantime/leantime/security/advisories/GHSA-qrfh-cc86-vc8c
- https://github.com/Leantime/leantime/commit/3f8b2c6346111694bb18cec558b27c22d3a2b9d1
- https://github.com/Leantime/leantime
