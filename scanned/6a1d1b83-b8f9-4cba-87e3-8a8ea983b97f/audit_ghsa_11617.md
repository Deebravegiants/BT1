# [H] AVideo has Session Fixation via GET PHPSESSID Parameter With Disabled Login Session Regeneration

## Summary
Severity: High
Advisory: GHSA-x3pr-vrhq-vq43
CVE: CVE-2026-33492
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-x3pr-vrhq-vq43
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

AVideo's `_session_start()` function accepts arbitrary session IDs via the `PHPSESSID` GET parameter and sets them as the active PHP session. A session regeneration bypass exists for specific blacklisted endpoints when the request originates from the same domain. Combined with the explicitly disabled session regeneration in `User::login()`, this allows a classic session fixation attack where an attacker can fix a victim's session ID before authentication and then hijack the authenticated session.

## Details

The vulnerability is a chain of three weaknesses that together enable session fixation:

### 1. Attacker-controlled session ID acceptance (`objects/functionsPHP.php:344-367`)

```php
function _session_start(array $options = [])
{
    // ...
    if (isset($_GET['PHPSESSID']) && !_empty($_GET['PHPSESSID'])) {
        $PHPSESSID = $_GET['PHPSESSID'];
        // ...
        if (!User::isLogged()) {
            if ($PHPSESSID !== session_id()) {
                _session_write_close();
                session_id($PHPSESSID);   // <-- sets session to attacker's ID
            }
            $session = @session_start($options);  // <-- starts with attacker's ID
```

The code reads `$_GET['PHPSESSID']` and programmatically calls `session_id($PHPSESSID)`, which bypasses both `session.use_only_cookies` and `session.use_strict_mode` PHP settings since the session ID is set via the PHP API, not via cookie/URL handling.

### 2. Session regeneration bypass for blacklisted endpoints (`objects/functionsPHP.php:375-378`, `objects/functions.php:3100-3116`)

```php
// functionsPHP.php:375-378
if (!blackListRegenerateSession()) {
    _session_regenerate_id();  // <-- SKIPPED when blacklisted + same-domain
}
```

```php
// functions.php:3100-3116
function blackListRegenerateSession()
{
    if (!requestComesFromSafePlace()) {
        return false;
    }
    $list = [
        'objects/getCaptcha.php',
        'objects/userCreate.json.php',
        'objects/videoAddViewCount.json.php',
    ];
    foreach ($list as $needle) {
        if (str_ends_with($_SERVER['SCRIPT_NAME'], $needle)) {
            return true;  // <-- regeneration skipped for these endpoints
        }
    }
    return false;
}
```

The `requestComesFromSafePlace()` check at `objects/functionsSecurity.php:182` only verifies that `HTTP_REFERER` matches the AVideo domain. When a victim clicks a link from within the AVideo platform (e.g., in a comment or video description), the browser naturally sets the Referer to the AVideo domain, satisfying this check.

### 3. Disabled session regeneration on login (`objects/user.php:1315-1317`)

```php
// Call custom session regenerate logic
// this was regenerating the session all the time, making harder to save info in the session
//_session_regenerate_id();  // <-- COMMENTED OUT
```

The session regeneration after authentication is explicitly disabled. This means the session ID persists unchanged through the login transition, which is the fundamental requirement for session fixation to succeed.

### Amplifying factors

- `objects/phpsessionid.json.php` exposes session IDs to any same-origin JavaScript without authentication (line 12: `$obj->phpsessid = session_id()`)
- `view/js/session.js` stores the session ID in a global `window.PHPSESSID` variable and logs it to console (line 15)
- No session-to-IP or session-to-user-agent binding exists (verified via codebase search)

## PoC

### Step 1: Attacker obtains a session ID

```bash
# Attacker visits the site to get a valid session ID
curl -v https://target.example.com/ 2>&1 | grep 'set-cookie.*PHPSESSID'
# Response: Set-Cookie: PHPSESSID=attacker_known_session_id; ...
```

### Step 2: Attacker injects a link on the platform

The attacker posts a comment on a video or creates content containing a link:

```
https://target.example.com/objects/getCaptcha.php?PHPSESSID=attacker_known_session_id
```

This can be placed in a video comment, video description, user bio, or forum post — anywhere AVideo renders user-provided links.

### Step 3: Victim clicks the link while browsing AVideo

When the victim clicks the link from within the AVideo platform:
1. Browser sets `Referer: https://target.example.com/...` (same-domain)
2. `_session_start()` processes `$_GET['PHPSESSID']`, victim is not logged in, so `session_id('attacker_known_session_id')` is called
3. `blackListRegenerateSession()` returns `true` (script is `getCaptcha.php` + same-domain Referer)
4. `_session_regenerate_id()` is **skipped**
5. Victim's session is now fixed to `attacker_known_session_id`

### Step 4: Victim logs in

The victim navigates to the login page and authenticates. `User::login()` populates `$_SESSION['user']` but does NOT regenerate the session ID (line 1317 is commented out).

### Step 5: Attacker hijacks the authenticated session

```bash
# Attacker uses the known session ID to access victim's account
curl -b "PHPSESSID=attacker_known_session_id" https://target.example.com/objects/user.php?userAPI=1
# Response: victim's user data, confirming session hijack
```

## Impact

- **Full account takeover**: An attacker can hijack any user's authenticated session, including administrator accounts
- **Data access**: Full access to the victim's videos, private content, messages, and personal information
- **Privilege escalation**: If the victim is an admin, the attacker gains full administrative control over the AVideo instance
- **Lateral actions**: The attacker can perform any action as the victim — upload/delete content, modify settings, access admin panel

## Recommended Fix

### Fix 1: Re-enable session regeneration on login (`objects/user.php:1317`)

```php
// Replace the commented-out line:
//_session_regenerate_id();

// With:
_session_regenerate_id();
```

This is the most critical fix. Session regeneration on authentication transition is a fundamental defense against session fixation (OWASP recommendation).

### Fix 2: Remove GET-based session ID acceptance (`objects/functionsPHP.php:344-383`)

Remove or restrict the `$_GET['PHPSESSID']` handling entirely. If it is needed for specific use cases (e.g., CAPTCHA), validate the session ID against a server-side token rather than blindly accepting arbitrary values:

```php
// Instead of accepting any GET PHPSESSID, remove this block entirely.
// If CAPTCHA requires session continuity, pass a CSRF token instead.
if (isset($_GET['PHPSESSID']) && !_empty($_GET['PHPSESSID'])) {
    // REMOVED: Do not accept session IDs from URL parameters
}
```

### Fix 3: Remove session ID exposure (`objects/phpsessionid.json.php`, `view/js/session.js`)

The `phpsessionid.json.php` endpoint and the `session.js` global variable negate the `httponly` cookie flag. If JavaScript needs to reference the session for AJAX requests, the browser automatically includes session cookies — there is no need to expose the session ID value to JavaScript.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-x3pr-vrhq-vq43
- https://nvd.nist.gov/vuln/detail/CVE-2026-33492
- https://github.com/WWBN/AVideo/commit/5647a94d79bf69a972a86653fe02144079948785
- https://github.com/WWBN/AVideo
