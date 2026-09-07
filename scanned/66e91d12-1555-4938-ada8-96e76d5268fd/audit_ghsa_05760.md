# [H] LibreNMS: SSRF-driven stored XSS via Oxidized API response fields in device showconfig page

## Summary
Severity: High
Advisory: GHSA-7gww-x7fh-jf9j
CWE: CWE-79, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-7gww-x7fh-jf9j
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <26.7.0

## Details
### Summary
The Oxidized integration URL (`oxidized.url`) is admin-configurable. LibreNMS fetches device info and version history from that URL and renders JSON fields (`name`, `ip`, `model`, `author`, commit message) into HTML without `htmlspecialchars()`. An admin pointing the URL at an attacker-controlled server achieves persistent XSS affecting all users who view any device's showconfig tab.

### CVSS
`CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:N` — **8.1 High**

### Details
```php
// includes/html/pages/device/showconfig.inc.php:276-278
echo '<li ...><strong>Node:</strong> ' . $node_info['name'] . '</li>';
echo '<li ...><strong>IP:</strong> '   . $node_info['ip']   . '</li>';
echo '<li ...><strong>Model:</strong> '. $node_info['model'] . '</li>';
// lines 349, 353: author and commit message also unescaped
```

### Attack chain
1. Admin sets `oxidized.url` to `http://attacker.example.com/`.
2. Attacker server returns `{"name":"<img src=x onerror=alert(1)>","ip":"x","model":"x"}`.
3. Any user viewing any device showconfig tab triggers the XSS.

### PoC
Mock Oxidized server confirmed in response:
```
[!!!] CONFIRMED — ...<strong>Node:</strong> <img src=x onerror="alert('SSRF-XSS-oxidized')">...
```

### Fix
```php
echo '<li ...><strong>Node:</strong> ' . htmlspecialchars($node_info['name'], ENT_QUOTES, 'UTF-8') . '</li>';
```
Apply to all fields from `$node_info`, `$author`, `$msg`.

### Prerequisite
Admin session. Oxidized integration must be enabled.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-7gww-x7fh-jf9j
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/26.7.0
