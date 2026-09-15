# [M] AVideo: Unauthenticated Arbitrary Image Read via Path Traversal in `view/img/image404Raw.php`

## Summary
Severity: Medium
Advisory: GHSA-w4qq-74h6-58wq
CVE: CVE-2026-46337
CWE: CWE-22, CWE-284, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-w4qq-74h6-58wq
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
### Summary
The endpoint requires **no authentication**. An unauthenticated remote attacker can read arbitrary image files anywhere on disk that the PHP user can open — including private user-profile photos that the application's normal serving wrappers gate behind ACLs, admin-uploaded thumbnails, encrypted-video poster frames, and image content under sibling-app directories reachable via `..` traversal.

### Details
`view/img/image404Raw.php` reads the `image` GET parameter and joins it directly into a filesystem path served via `readfile()`.  `view/img/image404Raw.php` (full file, current `master` @ `0dbadbcaaa1b415c7db078a72dc4b26d9fac0485`):

```php
<?php

// Fetch requested image URL
$imageURL = !empty($_GET['image']) ? $_GET['image'] : $_SERVER["REQUEST_URI"];
$rootDir = dirname(__FILE__) . '/../../';
if ($imageURL == 'favicon.ico') {
    $imgLocalFile = "{$rootDir}/videos/{$imageURL}";
} else {
    $imgLocalFile = "{$rootDir}/{$imageURL}";   // ← attacker-controlled
}

if (file_exists($imgLocalFile)) {
    $imageInfo = getimagesize($imgLocalFile);   // ← format gate
    if (empty($imageInfo)) {
        die('not image');
    }
    // …extension → Content-Type mapping…
    header("HTTP/1.0 200 OK");
    header('Content-Type: ' . $type);
    header('Content-Length: ' . filesize($imgLocalFile));
    readfile($imgLocalFile);   // ← exfil bytes
    exit;
}
```

Issues:

1. **No authentication.** The file is reachable via direct GET; no `require` of `globals.php`, no session check, no API-key gate.
2. **No basename / realpath / prefix containment.** `$_GET['image']`  is concatenated into `$imgLocalFile` with no `..` filtering, no `realpath()` resolution, no allowlist check against the intended `view/img/` directory.
3. **`getimagesize()` is a magic-bytes check, not a path constraint.**  Any file on disk whose first bytes match a recognized image format (`FFD8FF` JPEG, `89504E47` PNG, `474946` GIF, `52494646…57454250` WebP) passes the gate — including images stored outside any ACL'd area of the application.
4. **`$_SERVER["REQUEST_URI"]` fallback** when `image` is empty widens the attack surface (path components in the URI itself land in `$imgLocalFile`).

**Re-verified pre-submission** on 2026-05-13 against `view/img/image404Raw.php` blob SHA `c670b0faff4fbea1fd0508f179956975477d4340` — unsafe shape unchanged since first discovery on 2026-05-12.

**Recommended fix** — three layered checks, any one alone is insufficient:

```php
// view/img/image404Raw.php — proposed fix
<?php

$imageURL = !empty($_GET['image']) ? $_GET['image'] : '';
if ($imageURL === '') {
    http_response_code(400);
    exit('bad request');
}

// 1. Reject any path-traversal segment outright.
if (strpos($imageURL, '..') !== false
    || strpos($imageURL, "\0") !== false
    || strpos($imageURL, '://') !== false) {
    http_response_code(400);
    exit('bad request');
}

// 2. Resolve to a real path and verify prefix containment under the
//    intended image directory.
$rootDir = realpath(dirname(__FILE__) . '/../../');
$imgLocalFile = realpath($rootDir . '/' . $imageURL);
if ($imgLocalFile === false
    || (strpos($imgLocalFile, $rootDir . '/videos/') !== 0
        && strpos($imgLocalFile, $rootDir . '/view/img/') !== 0)) {
    http_response_code(404);
    exit('not found');
}

// 3. Existing getimagesize() check stays as defense-in-depth.
if (!is_file($imgLocalFile)) {
    http_response_code(404);
    exit('not found');
}
$imageInfo = @getimagesize($imgLocalFile);
if (empty($imageInfo)) {
    http_response_code(404);
    exit('not image');
}

// …rest of the original Content-Type + readfile() flow unchanged…
```

Drop the `$_SERVER["REQUEST_URI"]` fallback entirely; if no `image`
parameter is provided, return 400.

### PoC

Discovery probe — any HTTP client, no authentication, no cookies:

```http
GET /view/img/image404Raw.php?image=../videos/userPhoto/photo1.jpg HTTP/1.1
Host: avideo.example.com
```

If `videos/userPhoto/photo1.jpg` exists on the server, the response is the raw image bytes (HTTP 200, `Content-Type: image/jpeg`). The application's normal user-photo serving wrapper (which can gate by session / channel ownership) is bypassed entirely.

Cross-directory probe — read images outside the AVideo install root:

```http
GET /view/img/image404Raw.php?image=../../../var/www/other-app/uploads/users/admin.jpg HTTP/1.1
Host: avideo.example.com
```

If the PHP user has read access to a sibling app's image directory, those files are exfiltrable too.

Enumeration — iterate over predictable numeric IDs:

```
GET /view/img/image404Raw.php?image=../videos/userPhoto/photo1.jpg
GET /view/img/image404Raw.php?image=../videos/userPhoto/photo2.jpg
GET /view/img/image404Raw.php?image=../videos/userPhoto/photo3.jpg
...
```

…to harvest all profile images regardless of the application's intended privacy controls.

### Impact

**Path traversal → arbitrary image read (CWE-22 + CWE-284).** Affects any AVideo deployment running master through commit `0dbadbca` and likely every release on the supported branches. The attacker:

1. **Bypasses the application's image-content ACLs.** Profile photos under `videos/userPhoto/` and admin-uploaded private thumbnails  that AVideo's normal image-serving wrappers gate by session / channel ownership become readable to any anonymous internet user.
2. **Reads images stored outside the AVideo install root.** On shared-hosting / multi-tenant deployments, `..` traversal lets the  attacker page into sibling-app upload directories — anywhere the PHP user has read access on disk and the target file's first bytes form a valid image header.
3. **Enables enumeration at scale.** Numeric ID schemes (`photo1.jpg`, `photo2.jpg`, …) and predictable filenames let an attacker harvest every private image on a deployment without detection (each request looks like a single 200-image-OK to the web log).

Because the read primitive is restricted to image-magic-bytes files, there is no source-code or credential exfiltration via this primitive alone — but the **privacy / GDPR exposure** is substantial on any deployment that hosts user-uploaded photos. CVSS 5.3 (Medium) reflects the limited but real confidentiality impact; many operators will rate this higher because the leaked content is user-private by intent.

This is **not** a silent-fix disclosure — the bug is still present on current `master` at submission time; the maintainer is being
notified of a previously-unknown issue.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-w4qq-74h6-58wq
- https://nvd.nist.gov/vuln/detail/CVE-2026-46337
- https://github.com/WWBN/AVideo
