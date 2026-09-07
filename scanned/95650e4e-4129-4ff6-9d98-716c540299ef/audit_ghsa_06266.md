# [M] LibreNMS: Stored XSS via graph_descr admin config settings echoed without escaping to all authenticated users

## Summary
Severity: Medium
Advisory: GHSA-7cj5-v4pp-v632
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-7cj5-v4pp-v632
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <26.7.0

## Details
### Summary
The `graph_descr.<graphtype>` family of settings is echoed verbatim without `htmlspecialchars()` in `includes/html/pages/graphs.inc.php:194`. Any admin can store a malicious HTML payload that executes in every authenticated user's browser viewing that graph type.

### CVSS
`CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N` — **4.8 Medium**

### Details
```php
// graphs.inc.php:194
echo LibrenmsConfig::get('graph_descr.' . $vars['type']);
```

### PoC
```
PUT /settings/graph_descr.device_processor
{"value": "<img src=x onerror=\"alert('ADV-15')\">"}

GET /graphs?type=device_processor
→ <img src=x onerror="alert('ADV-15')">
```

### Fix
```php
echo htmlspecialchars(LibrenmsConfig::get('graph_descr.' . $vars['type']), ENT_QUOTES, 'UTF-8');
```

### Prerequisite
Admin session to set the config value.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-7cj5-v4pp-v632
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/26.7.0
