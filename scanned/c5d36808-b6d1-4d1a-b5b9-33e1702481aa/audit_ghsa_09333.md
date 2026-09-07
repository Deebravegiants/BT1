# [M] AVideo: Authenticated Arbitrary File Read in view/update.php

## Summary
Severity: Medium
Advisory: GHSA-3mjv-375j-6h92
CVE: CVE-2026-45731
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-3mjv-375j-6h92
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
### Summary
view/update.php reads $_POST['updateFile'] as a relative path under updatedb/ and passes it to PHP's file() for line-by-line execution as part of a database migration. An authenticated administrator can abuse this to read arbitrary text files reachable from the web-server process — especially valuable on misconfigured deployments where /etc/passwd, .env, or other sibling-app configs are reachable relative to the AVideo directory.

### Details
view/update.php, lines 134-145 (excerpt):

if (!empty($_POST['updateFile'])) {
    $dir = Video::getStoragePath() . "cache";
    rrmdir($dir);
    /* …unrelated cache-clear… */

    if (file_exists($logfile . "log")) {
        unlink($logfile . "log");
        // ...
    }
    $lines = file("{$global['systemRootPath']}updatedb/{$_POST['updateFile']}");
The User::isAdmin() and adminSecurityCheck(true) guards at lines 12-15 enforce admin auth, but $_POST['updateFile'] is concatenated into a path without any sanitization. file() returns the file's contents as an array of lines; the script subsequently iterates them and echoes the SQL it would run.

### PoC
POST /view/update.php
Content-Type: application/x-www-form-urlencoded

updateFile=../../../../etc/passwd
Result: the script attempts to load /etc/passwd (relative to {systemRootPath}updatedb/), echoing each line in the migration-runner HTML output. $_POST['updateFile'] traversal accepted, no extension guard, no in-array whitelist.

Attempting ../../../../proc/self/environ similarly reveals web-server environment variables on Linux.



### Impact
Verified on the current master branch of WWBN/AVideo (commit bc0340662…). Likely affected: every release where view/update.php contains the $_POST['updateFile'] consumer — pattern predates 2024.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-3mjv-375j-6h92
- https://nvd.nist.gov/vuln/detail/CVE-2026-45731
- https://github.com/WWBN/AVideo
