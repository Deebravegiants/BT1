# [M] AVideo: Unauthenticated Information Disclosure via Missing Auth on CloneSite client.log.php

## Summary
Severity: Medium
Advisory: GHSA-99j6-hj87-6fcf
CVE: CVE-2026-35452
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-99j6-hj87-6fcf
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `plugin/CloneSite/client.log.php` endpoint serves the clone operation log file without any authentication. Every other endpoint in the CloneSite plugin directory enforces `User::isAdmin()`. The log contains internal filesystem paths, remote server URLs, and SSH connection metadata.

## Details

The entire file at `plugin/CloneSite/client.log.php`:

```php
<?php
include '../../videos/cache/clones/client.log';
```

No authentication check. The log file is populated by `cloneClient.json.php` which writes operational details during clone operations:

```php
// plugin/CloneSite/cloneClient.json.php:118
$log->add("Clone (2 of {$totalSteps}): Geting MySQL Dump file [$cmd]");
```

The `$cmd` variable contains wget commands with internal filesystem paths, and rsync command templates with SSH connection details (username, IP, port).

Compare with sibling endpoints:
- `plugin/CloneSite/index.php` checks `User::isAdmin()`
- `plugin/CloneSite/changeStatus.json.php` checks `User::isAdmin()`
- `plugin/CloneSite/clones.json.php` checks `User::isAdmin()`
- `plugin/CloneSite/delete.json.php` checks `User::isAdmin()`

## Proof of Concept

```bash
curl "https://your-avideo-instance.com/plugin/CloneSite/client.log.php"
```

If the CloneSite feature has been used, the response contains wget commands, filesystem paths, SSH metadata, and SQL dump file locations.

## Impact

Unauthenticated disclosure of internal infrastructure details that could aid targeted attacks against the clone source server.

## Recommended Fix

Add an admin authentication check at `plugin/CloneSite/client.log.php`, before the include:

```php
require_once '../../videos/configuration.php';
if (!User::isAdmin()) {
    http_response_code(403);
    die('Access denied');
}
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-99j6-hj87-6fcf
- https://nvd.nist.gov/vuln/detail/CVE-2026-35452
- https://github.com/WWBN/AVideo
