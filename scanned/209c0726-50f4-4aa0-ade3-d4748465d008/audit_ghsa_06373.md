# [M] LibreNMS: Reflected XSS via Proxmox instance/vmid GET parameters injected into document.title JavaScript assignment

## Summary
Severity: Medium
Advisory: GHSA-jmqm-f8q4-v7wx
CVE: CVE-2026-45694
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-jmqm-f8q4-v7wx
Type: github-advisory

## Affected
- Packagist: `librenms/librenms` — affected >=0 <26.5.0

## Details
### Summary
`LegacyController.php:75` writes the page title into a `document.title` JS assignment using string interpolation. `apps/proxmox.inc.php` pushes `$vars['instance']` and `$vars['vmid']` (GET params, only `strip_tags()` applied) directly into `$pagetitle`. A single quote terminates the JS string, executing arbitrary script.

### Details
```php
// LegacyController.php:75
$html .= "<script>\ndocument.title = '$title';\n</script>";

// proxmox.inc.php:38,42
$pagetitle[] = $instance;     // GET ?instance=
$pagetitle[] = $vars['vmid']; // GET ?vmid=
```

### PoC
```
http://target/apps?app=proxmox&instance=%27%3Balert%28document.cookie%29%3B//

Confirmed in response:
document.title = 'Apps - Proxmox - ';alert(document.cookie);// - LibreNMS';
```

### Fix
```php
// LegacyController.php:75
$html .= "<script>\ndocument.title = " . json_encode($title) . ";\n</script>";
```
Also wrap `$instance` and `$vars['vmid']` in `htmlspecialchars()` in proxmox.inc.php.

### Prerequisite
Any authenticated session. Victim must follow a crafted link.

## References
- https://github.com/librenms/librenms/security/advisories/GHSA-jmqm-f8q4-v7wx
- https://github.com/librenms/librenms
- https://github.com/librenms/librenms/releases/tag/26.5.0
