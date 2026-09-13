# [M] AVideo: 2FA toggle endpoint has no CSRF protection, letting an attacker page silently disable a logged-in victim's 2FA

## Summary
Severity: Medium
Advisory: GHSA-3mv2-vmwh-rwfx
CVE: CVE-2026-45610
CWE: CWE-306, CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-3mv2-vmwh-rwfx
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
## Summary

**Type:** Cross-site request forgery on the 2FA toggle. `plugin/LoginControl/set.json.php` accepts `POST type=set2FA value=false`, calls `LoginControl::setUser2FA(User::getId(), false)` on the session-authenticated user, and returns. There is no `forbidIfIsUntrustedRequest()` call, no `isTokenValid()` check, no `X-CSRF-Token`/`SameSite` enforcement, and no re-authentication step. A cross-origin page that the victim visits while logged into the AVideo dashboard issues the POST via a hidden form (or `fetch` without `credentials:"omit"`) and disables the victim's 2FA in one request. The next phishing/credential-stuffing attempt against that account no longer needs the second factor.
**File:** `plugin/LoginControl/set.json.php`, lines 1-37.
**Root cause:** the developer relied on the `User::isLogged()` check at line 9 as the only auth, then dispatched directly into `LoginControl::setUser2FA(User::getId(), $value=='true')`. Other AVideo state-changing endpoints in the same codebase (`videoUpdateUsage.json.php`, `videoStatus.json.php`, `videoRotate.json.php`, etc.) call `forbidIfIsUntrustedRequest('<name>')` to compare `Origin`/`Referer` against the AVideo domain; this endpoint simply omits the call. The session cookie carries the user's identity on every cross-origin POST, so any attacker page can speak for the logged-in user on this endpoint.

## Affected Code

**File:** `plugin/LoginControl/set.json.php`, lines 1-37.

```php
<?php
require_once '../../videos/configuration.php';
_session_write_close();
header('Content-Type: application/json');

$obj = new stdClass();
$obj->error = true;
$obj->msg = "";
if (!User::isLogged()) {
    $obj->msg = "Not logged";
    die(json_encode($obj));
}
if (empty($_POST['type'])) {
    $obj->msg = "Type is empty";
    die(json_encode($obj));
}
if (!isset($_POST['value'])) {
    $obj->msg = "value is empty";
    die(json_encode($obj));
}

$cu = AVideoPlugin::loadPluginIfEnabled('LoginControl');

if (empty($cu)) {
    $obj->msg = "Plugin not enabled";
    die(json_encode($obj));
}

$obj->error = false;
switch ($_POST['type']) {
    case 'set2FA':
        LoginControl::setUser2FA(User::getId(), $_POST['value']=="true" ? true : false);  // <-- BUG: no CSRF gate, no re-auth
        break;
}

die(json_encode($obj));
```

**Why it's wrong:** disabling a victim's second factor is exactly the kind of state change the AVideo CSRF helper `forbidIfIsUntrustedRequest()` exists to protect. Compare with `objects/comments_like.json.php:18` (`forbidIfIsUntrustedRequest('comments_like')`) — comments-likes get CSRF protection, but the 2FA toggle does not. Beyond CSRF, security-sensitive toggles like 2FA-disable conventionally also require either the current 2FA code or a password re-prompt: a malicious browser extension, an XSS that lands in any AVideo subdomain, or a compromised tab can otherwise flip the bit silently. None of those mitigations exist here.

## Exploit Chain

1. Attacker hosts `https://attacker.example/avideo-2fa-off.html` containing:
   ```html
   <form id="f" action="https://avideo.example/plugin/LoginControl/set.json.php" method="POST">
     <input type="hidden" name="type"  value="set2FA">
     <input type="hidden" name="value" value="false">
   </form>
   <script>document.getElementById('f').submit();</script>
   ```
   State: page is live and indexable.
2. Attacker delivers the page to a victim who is logged in to `avideo.example` (open redirect on a trusted partner, ad campaign, IM phishing link, encyclopedic-looking forum post). The victim's browser opens the page; the form auto-submits to AVideo. State: cross-origin POST hits `set.json.php` with the victim's session cookie attached (the cookie's `SameSite` attribute is set to `Lax`/`None` by AVideo's defaults so the cross-origin POST succeeds for top-level navigations).
3. `set.json.php:9` confirms `User::isLogged()` (true, victim's session is valid). Lines 13-19 see `type=set2FA`, `value=false`. Line 30-32 calls `LoginControl::setUser2FA(victim_user_id, false)` and persists the change. State: victim's 2FA is now disabled in `users.externalOptions.LoginControl.is2FAEnabled`.
4. Victim sees a generic "operation completed" JSON response in a redirected browser tab (or no visible feedback at all if the form lands in an `iframe`). State: victim notices nothing unusual.
5. Attacker (in a separate session) attempts credential stuffing or password-spray against `avideo.example/objects/login.json.php`. Without the second factor, any one of: a previously leaked password, a successful credential-stuffing match, or a spear-phishing-collected password completes the login. State: attacker holds full session for victim's account.
6. Final state: the second factor that the victim explicitly enabled was silently disabled across the wire by visiting an attacker-hosted page. The whole chain takes one HTTP POST and zero clicks beyond the initial visit.

## Security Impact

**Severity:** sec-moderate. CVSS 6.5: network attack, low complexity, low privileges (the attacker themselves are unauthenticated; the victim must be a logged-in AVideo user; this is captured by `PR:L` because the action's effect requires the victim's session), user interaction required (visit attacker page), scope unchanged, no confidentiality directly, high integrity (the victim's 2FA configuration is silently corrupted), no availability claim.
**Attacker capability:** with one cross-origin POST, the attacker turns a victim's 2FA-protected account into a plain password-only account. Combined with any password leak, credential-stuffing match, or successful phishing of the password, the account is fully compromised. The change is permanent until the victim notices and re-enables 2FA, and AVideo does not raise an audit-log event when 2FA is disabled (see `LoginControl::setUser2FA` — it simply writes the boolean), so detection is unlikely.
**Preconditions:** AVideo deployment with the `LoginControl` plugin enabled (the plugin shipping the 2FA feature); the victim is logged in to AVideo at the moment they visit the attacker page; the AVideo session cookie does not have `SameSite=Strict` (the deployment default is `SameSite=Lax` per `objects/phpsessionid.json.php:53`, which still allows cross-origin top-level POSTs from a form auto-submit).
**Differential:** source-inspection-verified. `set.json.php` does not contain `forbidIfIsUntrustedRequest`, `isTokenValid`, `verifyToken`, or any equivalent string; the entire body of the file is reproduced above. With the suggested fix below, the same cross-origin POST returns a 403 with `Invalid Request` and the `setUser2FA` call never fires.

## Suggested Fix

Add the same CSRF gate every other state-changing endpoint in this codebase uses, and require the current 2FA code (or a password re-prompt) when the user is *disabling* the second factor.

```diff
--- a/plugin/LoginControl/set.json.php
+++ b/plugin/LoginControl/set.json.php
@@ -9,6 +9,8 @@
 if (!User::isLogged()) {
     $obj->msg = "Not logged";
     die(json_encode($obj));
 }
+forbidIfIsUntrustedRequest('LoginControl-set');
+
 if (empty($_POST['type'])) {
     $obj->msg = "Type is empty";
     die(json_encode($obj));
@@ -28,7 +30,15 @@
 $obj->error = false;
 switch ($_POST['type']) {
     case 'set2FA':
-        LoginControl::setUser2FA(User::getId(), $_POST['value']=="true" ? true : false);
+        $newValue = ($_POST['value'] == 'true');
+        // Require the current 2FA code (or a password re-prompt) when DISABLING 2FA;
+        // turning it on is fine, turning it off needs a step-up.
+        if (!$newValue && !LoginControl::confirmStepUpForCurrentUser($_POST['confirm'] ?? '')) {
+            $obj->error = true;
+            $obj->msg = __('Re-authentication required to disable 2FA');
+            die(json_encode($obj));
+        }
+        LoginControl::setUser2FA(User::getId(), $newValue);
         break;
 }
```

Defence-in-depth: the AVideo session cookie should be issued with `SameSite=Strict` for the management dashboard's first-party POSTs; the public read-only player can keep a separate `SameSite=Lax` cookie. Audit-log every 2FA-disable event with the source IP and user agent so an unexpected disable is visible to the operator.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-3mv2-vmwh-rwfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45610
- https://github.com/WWBN/AVideo
