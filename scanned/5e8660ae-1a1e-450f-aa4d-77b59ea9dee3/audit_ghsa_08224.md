# [H] AVideo's Meet plugin: `uploadRecordedVideo.json.php` derives `users_id` from the uploaded filename and calls passwordless `User->login()`, allowing any caller with the Meet shared secret to obtain a session as arbitrary users including admin

## Summary
Severity: High
Advisory: GHSA-qxvm-r42f-5p8j
CWE: CWE-1390, CWE-287, CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-qxvm-r42f-5p8j
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
## Summary

**Type:** Authorization-bypass via user-controlled identifier. The Meet plugin's recorded-video upload endpoint (`plugin/Meet/uploadRecordedVideo.json.php`) authenticates the caller using a single shared `Authorization: Bearer <secret>` against `$objM->secret`. Once that check passes, the endpoint reads the *target user identifier* from the uploaded file's `name` field, instantiates a `User` object with that ID, and calls `$userObject->login(true, true)` — the no-password / encoded-password login path — committing a session for that user and emitting `Set-Cookie` headers to the caller. There is no check that the caller actually owns the requested `users_id`.
**File:** `plugin/Meet/uploadRecordedVideo.json.php`, lines 56-65; secondary in `objects/user.php` `User::login()` (no-password branch at lines 1276-1310).
**Root cause:** the upload handler's identity model is "service-to-service" (a Meet/Jitsi recorder posts a finished recording back to AVideo with the shared secret) but the `users_id` to credit the upload to is parsed from the FILENAME the same caller controls — `$users_id = explode('-', $_FILES['upl']['name'])[0];`. There is no signed claim, no separate proof-of-identity, no allowlist. The subsequent `$userObject->login(true, true)` call invokes the no-password login path which sets `$_SESSION['user']`, calls `setUserCookie(...)`, and `_session_regenerate_id()` — exactly the operations a normal login performs. The response carries the new `PHPSESSID` back to the caller, who can then reuse it on every subsequent request to act as the targeted user. The Meet shared secret is `md5($global['systemRootPath'] . $global['salt'] . "meet")` (`Meet.php:73`), so any attacker who can read `videos/configuration.php` (e.g., via a path-traversal CVE such as `GHSA-83xq-8jxj-4rxm` or `GHSA-4wmm-6qxj-fpj4` that the project has already addressed in this surface area) can compute the Meet secret deterministically and pivot to full account takeover.

## Affected Code

**File:** `plugin/Meet/uploadRecordedVideo.json.php`, lines 33-73.

```php
if (empty($token)) {
    forbiddenPage('Token not found');
}

$objM = AVideoPlugin::getObjectDataIfEnabled("Meet");
if (empty($objM)) {
    forbiddenPage('Plugin disabled');
}

if ($objM->secret != $token) {                              // <-- shared-secret auth, no per-user proof
    forbiddenPage('Token does not match');
}

if (empty($_FILES['upl'])) {
    forbiddenPage('videoFile not found');
}

$users_id = explode('-', $_FILES['upl']['name'])[0];        // <-- BUG: target users_id parsed from attacker-controlled filename

$userObject = new User($users_id);
$userObject->login(true, true);                             // <-- BUG: passwordless login as the chosen user; sets $_SESSION + Set-Cookie
$tmpFile = getTmpDir() . uniqid();

if (move_uploaded_file($_FILES['upl']['tmp_name'], $tmpFile)) {
    $_FILES['upl']['tmp_name'] = $tmpFile;
    require $global['systemRootPath'] . 'objects/aVideoQueueEncoder.json.php';
}
```

**File:** `objects/user.php`, lines 1249-1329 (`User::login()` no-password branch).

```php
public function login($noPass = false, $encodedPass = false, $ignoreEmailVerification = false)
{
    // ...
    if ($noPass) {
        $user = $this->find($this->user, false, true);      // <-- no password check
    }
    // ...
    } elseif ($user) {
        $_SESSION['user'] = $user;                          // <-- session set for the impersonated user
        $this->setLastLogin($_SESSION['user']['id']);
        // ...
        self::setUserCookie($rememberme, $user['id'], $user['user'], $passhash, $expires);
        AVideoPlugin::onUserSignIn($_SESSION['user']['id']);
        $_SESSION['loginAttempts'] = 0;
        _session_regenerate_id();                           // <-- new SID committed in Set-Cookie response
        _session_write_close();
        return self::USER_LOGGED;
    }
}
```

**Why it's wrong:** the endpoint conflates two distinct authentication concerns. The shared-secret check answers "is this request coming from a trusted Meet recorder?" but the filename parse answers "which user does this recording belong to?" — and the second answer is taken from the same untrusted caller. Once `User->login(true, true)` runs, the server has no way to distinguish a legitimate Meet integration from an attacker who happens to know the same secret. The decision to expose this as a session (cookie + `_session_regenerate_id`) rather than as a one-shot in-process credit makes the impact larger than it needs to be: even if the Meet integration only needed to *credit* the recording to a user, the implementation gives the caller a fully-authenticated session as that user.

## Exploit Chain

1. Attacker obtains the Meet shared secret. Two plausible paths:
   - **Path A** (computational): the secret is `md5($global['systemRootPath'] . $global['salt'] . "meet")` (`plugin/Meet/Meet.php:73`). Both inputs sit in `videos/configuration.php`. AVideo's history of LFI/path-traversal CVEs in this surface (e.g., the `import.json.php` and `listFiles.json.php` advisories already accepted on this program) means the salt is a realistic disclosure target.
   - **Path B** (timing oracle): `plugin/Meet/checkToken.json.php` line 26 does `if ($objM->secret === $_GET['secret'])` with no constant-time comparison and a clear yes/no response body. PHP's `===` for strings short-circuits on first byte mismatch, so an attacker on the same network segment can recover the 32-hex secret byte-by-byte over the network with timing analysis. Slower than path A but doesn't depend on a separate vulnerability.
2. Attacker prepares an HTTP POST to `/plugin/Meet/uploadRecordedVideo.json.php`:
   - `Authorization: Bearer <Meet secret>`
   - Multipart body with one file field named `upl`. The filename is set to `1-anything.mp4` (where `1` is the `users_id` of the admin or any target user — the format is `<users_id>-<arbitrary>`). The file body itself can be anything that survives the surrounding aVideoQueueEncoder pipeline (an empty file is enough to reach the login call before the encoder rejects).
3. Server flow:
   - Line 33: token present, ok.
   - Line 46: `$objM->secret != $token` → false (matches), passes.
   - Line 51: `$_FILES['upl']` present, ok.
   - Line 56: `$users_id = explode('-', '1-anything.mp4')[0]` → `'1'`.
   - Line 59-60: `$userObject = new User(1); $userObject->login(true, true);` — passwordless login as user 1 (admin). `$_SESSION['user']` is set, `setUserCookie` runs, `_session_regenerate_id` issues a new session ID, and the response carries `Set-Cookie: PHPSESSID=<new-sid>; ...`.
   - Subsequent code runs the encoder pipeline as admin — but the attacker's primary goal was already achieved when the session was established.
4. Attacker captures the `Set-Cookie: PHPSESSID=...` header from the response and uses that cookie on all subsequent requests. Server treats them as user 1 (admin) — full UI access, all admin endpoints, all video management, plugin configuration, user impersonation, etc.
5. Final state: admin account takeover. The original Meet recorder's flow (legitimate uploads with `users_id` = the user who scheduled the meeting) is indistinguishable on the wire from the attack flow (`users_id` = whoever the attacker wants to be).

## Security Impact

**Severity:** sec-high. End state is full account takeover of any user (including admin), reachable from a single HTTP POST once the secret is known. The shared-secret precondition raises AC to High but does not eliminate it as a credible threat — the secret is computable from any leak of `videos/configuration.php`, and AVideo's CVE history in that surface area is non-trivial.
**Attacker capability:** session hijack as any `users_id` the attacker cares to name. The attacker chooses the target by setting the filename's leading digits before the first `-`. No bound on which user IDs are reachable; admin (`1` on a default install) is the obvious target. Once the session is captured, the attacker has full admin UI/API access for the session lifetime (hours-to-days depending on `rememberme` flag).
**Preconditions:** Meet plugin enabled (default-off but commonly enabled by deployments using AVideo for video-conferencing recording). Knowledge of the Meet shared secret (computable from the salt; obtainable via timing attack on `checkToken.json.php`).
**Differential:** source-inspection-verified end-to-end. The two relevant code blocks are quoted verbatim in §Affected Code; both lines are reachable on every successful POST to the endpoint. The patched build (with the suggested fix below) either rejects the upload as `'cannot derive identity from filename'` or constrains the `users_id` to one bound by an additional signed claim from the Meet recorder.

## Suggested Fix

Three changes, in order of importance:

```diff
--- a/plugin/Meet/uploadRecordedVideo.json.php
+++ b/plugin/Meet/uploadRecordedVideo.json.php
@@ -53,17 +53,28 @@ if (empty($_FILES['upl'])) {
     forbiddenPage('videoFile not found');
 }

-$users_id = explode('-', $_FILES['upl']['name'])[0];
+// The users_id MUST come from a signed claim (e.g., a JWT issued by AVideo
+// when the meeting was scheduled), not from a filename the caller controls.
+// Verify a recording-upload token here that was minted at meeting-create
+// time and bound to (meet_schedule_id, users_id) with an HMAC.
+$claim = MeetUploadClaim::verifyFromHeaders($headers);
+if (!$claim) {
+    forbiddenPage('Missing or invalid recording upload claim');
+}
+$users_id = (int) $claim->users_id;
+if (!$users_id || !User::idExists($users_id)) {
+    forbiddenPage('Recording upload claim references unknown user');
+}

-$userObject = new User($users_id);
-$userObject->login(true, true);
+// Credit the upload to $users_id WITHOUT establishing a session. The encoder
+// pipeline can be parameterised to record ownership directly; there is no
+// reason for a service-to-service upload endpoint to mint a user session.
+$queueOwnerUsersId = $users_id;
 $tmpFile = getTmpDir() . uniqid();

 if (move_uploaded_file($_FILES['upl']['tmp_name'], $tmpFile)) {
     $_FILES['upl']['tmp_name'] = $tmpFile;
-    require $global['systemRootPath'] . 'objects/aVideoQueueEncoder.json.php';
+    aVideoQueueEncoder::encodeOnBehalfOf($queueOwnerUsersId, $_FILES['upl']);
 }
```

Additionally:

1. **Use `hash_equals` for the secret comparison** in both this endpoint and `checkToken.json.php` (`if (!hash_equals($objM->secret, $token))`). The current `==`/`===` is vulnerable to byte-by-byte timing analysis.
2. **Remove `checkToken.json.php` entirely**, or at least gate it behind `User::isAdmin()`. A network-reachable endpoint that confirms whether a guess matches the server-side secret is exactly the wrong shape for a high-value secret like this one.

Optional defense-in-depth (separate change): rotate the Meet secret to use a random 256-bit value (not derived from `salt`), so a `videos/configuration.php` disclosure does not also yield the Meet secret. Store the random secret as a per-deployment row in the Meet plugin's configuration table, generated at first-run.

Add a regression test: call `uploadRecordedVideo.json.php` with the correct secret but a filename of `1-x.mp4`; assert the response does NOT include a `Set-Cookie: PHPSESSID=` header.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-qxvm-r42f-5p8j
- https://github.com/WWBN/AVideo
