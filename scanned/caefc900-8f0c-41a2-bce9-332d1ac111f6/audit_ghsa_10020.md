# [M] AVideo: Unauthenticated FFmpeg Remote Server Status Disclosure via check.ffmpeg.json.php

## Summary
Severity: Medium
Advisory: GHSA-2vg4-rrx4-qcpq
CVE: CVE-2026-35450
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-2vg4-rrx4-qcpq
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `plugin/API/check.ffmpeg.json.php` endpoint probes the FFmpeg remote server configuration and returns connectivity status without any authentication. All sibling FFmpeg management endpoints (`kill.ffmpeg.json.php`, `list.ffmpeg.json.php`, `ffmpeg.php`) require `User::isAdmin()`.

## Details

The entire file at `plugin/API/check.ffmpeg.json.php`:

```php
<?php
$configFile = __DIR__.'/../../videos/configuration.php';
require_once $configFile;
header('Content-Type: application/json');

$obj = testFFMPEGRemote();

die(json_encode($obj));
```

No `User::isAdmin()`, `User::isLogged()`, or any access control check exists.

Compare with sibling endpoints in the same directory:
- `kill.ffmpeg.json.php` checks `User::isAdmin()`
- `list.ffmpeg.json.php` checks `User::isAdmin()`

## Proof of Concept

```bash
curl "https://your-avideo-instance.com/plugin/API/check.ffmpeg.json.php"
```

Returns information about whether the platform uses a standalone FFmpeg server and its current reachability.

## Impact

Infrastructure reconnaissance revealing the encoding architecture. Limited direct impact but aids targeted attack planning.

## Recommended Fix

Add an admin authentication check at `plugin/API/check.ffmpeg.json.php:3`, after `require_once $configFile;`:

```php
if (!User::isAdmin()) {
    forbiddenPage('Admin only');
}
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-2vg4-rrx4-qcpq
- https://nvd.nist.gov/vuln/detail/CVE-2026-35450
- https://github.com/WWBN/AVideo
