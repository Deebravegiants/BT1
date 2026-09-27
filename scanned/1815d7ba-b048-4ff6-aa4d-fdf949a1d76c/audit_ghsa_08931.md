# [M] AVideo: CSRF in userSavePhoto.php Allows Cross-Origin Overwrite of Authenticated Users' Profile Photos with Arbitrary Content

## Summary
Severity: Medium
Advisory: GHSA-jw8g-5j46-44rp
CVE: CVE-2026-43877
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-jw8g-5j46-44rp
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

`objects/userSavePhoto.php` is a legacy profile-photo endpoint that accepts a base64 POST parameter and writes the decoded bytes to `videos/userPhoto/photo<users_id>.png`. Its only access control is `User::isLogged()`. It does not end in `.json.php`, so it is excluded from the project's global `autoCSRFGuard` (which is suffix-scoped in `objects/include_config.php`). There is no CSRF token, no Origin/Referer check, and no MIME validation of the decoded bytes. Because AVideo's default cookie policy is `SameSite=None; Secure` on HTTPS (`objects/functionsPHP.php:227`), an attacker who lures a logged-in user to a malicious page can overwrite that user's profile photo with arbitrary bytes and also triggers a site-wide `clearCache(true)` on every forged request.

## Details

Handler (`objects/userSavePhoto.php`, 51 lines total):

```php
// line 12 - only access control
if (!User::isLogged()) {
    $obj->msg = __("You must be logged");
    die(json_encode($obj));
}
// ...
// line 29 - unvalidated base64 from POST
$fileData = base64DataToImage($_POST['imgBase64']);
// line 30 - deterministic filename tied to the VICTIM's session
$fileName = 'photo'. User::getId().'.png';
$photoURL = $imagePath.$fileName;
// line 35 - raw bytes written to disk
$bytes = file_put_contents($global['systemRootPath'].$photoURL, $fileData);
// lines 43-48 - DB update + global cache invalidation unconditionally
$user = new User(User::getId());
$user->setPhotoURL($photoURL);
if ($user->save()) {
    User::deleteOGImage(User::getId());
    User::updateSessionInfo();
    clearCache(true);
}
```

`base64DataToImage` (`objects/functionsImages.php:1026`) performs no content validation:

```php
function base64DataToImage($imgBase64) {
    $img = $imgBase64;
    $img = str_replace('data:image/png;base64,', '', $img);
    $img = str_replace(' ', '+', $img);
    return base64_decode($img);
}
```

There is no call to `getimagesizefromstring`, `imagecreatefromstring`, or MIME detection. Arbitrary bytes up to `post_max_size` are accepted.

**Why the global CSRF guard does not apply.** `objects/include_config.php` (around line 314) only invokes `autoCSRFGuard` when the script filename matches `*.json.php`:

```php
if (... $_SERVER['REQUEST_METHOD'] === 'POST' &&
    substr($baseName, -9) === '.json.php') {
    autoCSRFGuard($baseName, $_SERVER['SCRIPT_FILENAME']);
}
```

`userSavePhoto.php` is missing the `.json.php` suffix, so neither `autoCSRFGuard` nor `forbidIfIsUntrustedRequest` runs. There is no explicit call to any of these in the file (verified by grep: no `getCSRF`, no `forbidIfIsUntrustedRequest`, no `HTTP_ORIGIN`, no `HTTP_REFERER`). Routing rewrites in `.htaccess` also expose this handler as `/savePhoto`.

**Why the victim's cookie is sent cross-origin.** `objects/functionsPHP.php:227`:

```php
function _getCookieSameSiteValue($secure) {
    return $secure ? 'None' : 'Lax';
}
```

On HTTPS (the expected deployment), session cookies default to `SameSite=None; Secure`, which browsers attach to cross-site POSTs. A plain `application/x-www-form-urlencoded` form POST is a "simple request" under CORS rules and does not trigger a preflight, so the browser sends the POST and its cookie without the server having to opt in.

## PoC

1. Victim logs into the AVideo instance (e.g., `https://victim.example.com`). `PHPSESSID` is set with `SameSite=None; Secure`.
2. Attacker hosts the following HTML on any domain:

```html
<!doctype html>
<html><body>
<form id="f" action="https://victim.example.com/objects/userSavePhoto.php" method="POST">
  <!-- Any bytes: here, 'HELLO WORLD' base64-encoded -->
  <input name="imgBase64" value="SEVMTE8gV09STEQ=">
</form>
<script>document.forms[0].submit();</script>
</body></html>
```

3. Victim visits the attacker page in the same browser. The form auto-submits. The browser sends the POST with the victim's session cookie.
4. `userSavePhoto.php` passes the `User::isLogged()` check, decodes the base64, and writes the raw bytes to `videos/userPhoto/photo<VICTIM_USERS_ID>.png`. It also calls `$user->save()`, `User::deleteOGImage()`, `User::updateSessionInfo()`, and `clearCache(true)`.
5. Fetching `https://victim.example.com/videos/userPhoto/photo<VICTIM_USERS_ID>.png` (the file is now the attacker's bytes — `HELLO WORLD` in this test case). The response is `200 OK` and the body equals the submitted bytes.

Replace the `imgBase64` payload with a valid PNG to make the defacement visually persuasive, or with up to ~6 MB of any bytes to force a large write.

## Impact

- **Integrity — profile defacement of any logged-in user.** One click lets an attacker replace a victim's profile photo with arbitrary bytes: offensive imagery, misleading branding, or a clone of another user's photo for impersonation. The file path is deterministic (`photo<users_id>.png`), so the attacker can later direct others to the overwritten URL.
- **Availability — global cache thrash.** Every successful forged request calls `clearCache(true)`, invalidating application-wide caches. Repeatedly tricking logged-in users into visiting the attacker page (e.g., by including the payload as a hidden iframe on a popular site) produces sustained cache invalidation.
- **Availability — disk pressure.** With no size cap beyond PHP's `post_max_size` (default 8 MB → ~6 MB after base64 decode), each forged submission writes a multi-megabyte file. Across many victims this enables distributed disk exhaustion.
- **No confidentiality impact** and no code execution (files are served with `Content-Type: image/png` based on extension, so SVG-with-script payloads are not interpreted).
- **Related endpoints.** `objects/userSaveBackground.php` exhibits the same pattern (same `base64DataToImage` sink, same lack of CSRF/Origin/MIME checks) and is exploitable identically; fix should be applied consistently.

## Recommended Fix

Apply the existing same-origin guard that protects the `*.json.php` endpoints and add content validation. In `objects/userSavePhoto.php`, immediately after the login check:

```php
require_once $global['systemRootPath'] . 'objects/functionsSecurity.php';
forbidIfIsUntrustedRequest('userSavePhoto');

$raw = $_POST['imgBase64'] ?? '';
if (strlen($raw) > 2 * 1024 * 1024) { // ~1.5 MB decoded cap
    $obj->msg = __('Image too large');
    die(json_encode($obj));
}
$fileData = base64DataToImage($raw);
if ($fileData === false || $fileData === '' || @imagecreatefromstring($fileData) === false) {
    $obj->msg = __('Invalid image');
    die(json_encode($obj));
}
```

The longer-term fix is to broaden the global guard in `objects/include_config.php` so that `autoCSRFGuard` covers every authenticated POST handler, not only those whose filenames end in `.json.php` — the current suffix-based gating is a footgun that silently excludes legacy endpoints like `userSavePhoto.php` and `userSaveBackground.php`. Also consider moving the `clearCache(true)` call inside the `if ($bytes)` branch so that zero-byte writes do not invalidate the global cache.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-jw8g-5j46-44rp
- https://nvd.nist.gov/vuln/detail/CVE-2026-43877
- https://github.com/WWBN/AVideo/commit/9c38468041505e637101c5943c5370c68f48e3ac
- https://github.com/WWBN/AVideo
