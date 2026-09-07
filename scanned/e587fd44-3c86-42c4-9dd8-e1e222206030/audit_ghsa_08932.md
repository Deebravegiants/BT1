# [M] AzuraCast's Missing RequireInternalConnection on Liquidsoap API Allows Low-Privilege Metadata Injection and Broadcast Disruption

## Summary
Severity: Medium
Advisory: GHSA-4fm3-ggg2-c6qx
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-4fm3-ggg2-c6qx
Type: github-advisory

## Affected
- Packagist: `azuracast/azuracast` — affected >=0 <0.23.6

## Details
## Summary

The `/api/internal/{station_id}/liquidsoap/{action}` endpoint is accessible from the public web interface because it lacks the `RequireInternalConnection` middleware that protects other internal endpoints (`/sftp-auth`, `/sftp-event`). Combined with a logic flaw where the `$asAutoDj` flag is set based on the *presence* of the `X-Liquidsoap-Api-Key` header rather than its *validated value*, any user with the basic `View` station permission can invoke privileged Liquidsoap commands — injecting arbitrary now-playing metadata visible to all listeners, disrupting live broadcast tracking, and disclosing absolute filesystem paths.

## Details

**Issue 1: Missing RequireInternalConnection middleware**

In `backend/config/routes/api_internal.php`, the liquidsoap route group (lines 17-21) lacks the `RequireInternalConnection` middleware:

```php
// Lines 17-21 — NO RequireInternalConnection
$group->map(
    ['GET', 'POST'],
    '/liquidsoap/{action}',
    Controller\Api\Internal\LiquidsoapAction::class
)->setName('api:internal:liquidsoap');
```

Compare with sftp endpoints that correctly apply it:

```php
// Lines 32-34 — HAS RequireInternalConnection
$group->post('/sftp-auth', Controller\Api\Internal\SftpAuthAction::class)
    ->setName('api:internal:sftp-auth')
    ->add(Middleware\RequireInternalConnection::class);
```

The nginx config (`util/docker/web/nginx/azuracast.conf.tmpl`) only sets the `IS_INTERNAL` FastCGI parameter on the internal port 6010 listener (line 44), not on the public-facing server block (ports 80/443). Without the middleware, the endpoint is fully accessible from the public internet.

**Issue 2: `$asAutoDj` derived from header presence, not validated value**

In `backend/src/Controller/Api/Internal/LiquidsoapAction.php`:

```php
// Line 34 — checks header PRESENCE, not value
$asAutoDj = $request->hasHeader('X-Liquidsoap-Api-Key');

// Lines 38-44 — key value only checked when ACL FAILS
$acl = $request->getAcl();
if (!$acl->isAllowed(StationPermissions::View, $station->id)) {
    $authKey = $request->getHeaderLine('X-Liquidsoap-Api-Key');
    if (!$station->validateAdapterApiKey($authKey)) {
        throw new RuntimeException('Invalid API key.');
    }
}
```

When a user authenticates via session/API key and has `StationPermissions::View`, the ACL check passes and the adapter API key is never validated. But `$asAutoDj` is already `true` from line 34 because the header is present (with any arbitrary value).

**Affected commands:**

- `FeedbackCommand` (`backend/src/Radio/Backend/Liquidsoap/Command/FeedbackCommand.php:36`): Guard `if (!$asAutoDj) return false;` bypassed — creates SongHistory records and forces NowPlaying cache updates
- `DjOffCommand` (`backend/src/Radio/Backend/Liquidsoap/Command/DjOffCommand.php:24`): Guard bypassed — calls `$this->streamerRepo->onDisconnect($station)` which ends all active broadcasts and sets `$station->is_streamer_live = false`
- `DjOnCommand` (`backend/src/Radio/Backend/Liquidsoap/Command/DjOnCommand.php:31`): Guard bypassed — calls `$this->streamerRepo->onConnect($station, $user)` with attacker-controlled username
- `CopyCommand` (`backend/src/Radio/Backend/Liquidsoap/Command/CopyCommand.php:18`): No `$asAutoDj` guard at all — returns absolute filesystem paths via `$mediaFs->getLocalPath($uri)`

## PoC

**Prerequisites:** A user account with `StationPermissions::View` on station ID 1 (the lowest station-level permission). Obtain a session cookie or API key for this user.

**1. Inject arbitrary now-playing metadata (FeedbackCommand):**

```bash
curl -X POST 'https://target/api/internal/1/liquidsoap/feedback' \
  -H 'X-API-Key: <view-user-api-key>' \
  -H 'X-Liquidsoap-Api-Key: anything' \
  -H 'Content-Type: application/json' \
  -d '{"artist": "INJECTED", "title": "Fake Song Title"}'
```

Expected: Should reject — user does not have the adapter API key.
Actual: Returns `true`. The injected artist/title appears in `/api/nowplaying/1` for all listeners.

**2. Disrupt live broadcast (DjOffCommand):**

```bash
curl -X POST 'https://target/api/internal/1/liquidsoap/djoff' \
  -H 'X-API-Key: <view-user-api-key>' \
  -H 'X-Liquidsoap-Api-Key: anything'
```

Expected: Should reject.
Actual: Returns `true`. All active broadcast records for the station are terminated (`timestampEnd` set), `is_streamer_live` set to `false`, and `current_streamer` cleared.

**3. Disclose filesystem paths (CopyCommand):**

```bash
curl -X POST 'https://target/api/internal/1/liquidsoap/cp' \
  -H 'X-API-Key: <view-user-api-key>' \
  -H 'Content-Type: application/json' \
  -d '{"uri": "test.mp3"}'
```

Expected: Should reject — this is an internal-only endpoint.
Actual: Returns `{"uri":"/var/azuracast/stations/1/media/test.mp3","isTemp":false}` — disclosing the absolute filesystem path of the station's media storage.

## Impact

Any user with the basic `StationPermissions::View` permission (the lowest station-level role, commonly assigned to DJs and collaborators) can:

1. **Inject arbitrary now-playing metadata** visible to all listeners via the public NowPlaying API and any connected players/widgets. This poisons the song history database and triggers cache updates that propagate the false data to all consumers.

2. **Disrupt live broadcasts** by terminating all active broadcast records and marking the station as having no live streamer, even when a DJ is actively broadcasting. This affects broadcast recording and live-DJ tracking.

3. **Fake DJ connections** with arbitrary usernames via the `djon` command, polluting streamer logs and potentially interfering with DJ scheduling.

4. **Disclose absolute filesystem paths** of the station's media storage directory via the `cp` command (no `$asAutoDj` guard required), which aids further attacks against the server.

## Recommended Fix

**Fix 1: Add `RequireInternalConnection` middleware to the liquidsoap route group.**

In `backend/config/routes/api_internal.php`, add the middleware to the station group:

```php
$group->group(
    '/{station_id}',
    function (RouteCollectorProxy $group) {
        $group->map(
            ['GET', 'POST'],
            '/liquidsoap/{action}',
            Controller\Api\Internal\LiquidsoapAction::class
        )->setName('api:internal:liquidsoap')
+           ->add(Middleware\RequireInternalConnection::class);

        // Icecast internal auth functions
        $group->map(
            ['GET', 'POST'],
            '/listener-auth[/{api_auth}]',
            Controller\Api\Internal\ListenerAuthAction::class
        )->setName('api:internal:listener-auth');
    }
)->add(Middleware\GetStation::class);
```

**Fix 2: Validate the API key value before setting `$asAutoDj`.**

In `backend/src/Controller/Api/Internal/LiquidsoapAction.php`, move `$asAutoDj` assignment after key validation:

```php
- $asAutoDj = $request->hasHeader('X-Liquidsoap-Api-Key');
+ $asAutoDj = false;

  try {
      $acl = $request->getAcl();
      if (!$acl->isAllowed(StationPermissions::View, $station->id)) {
          $authKey = $request->getHeaderLine('X-Liquidsoap-Api-Key');
          if (!$station->validateAdapterApiKey($authKey)) {
              throw new RuntimeException('Invalid API key.');
          }
+         $asAutoDj = true;
+     } else {
+         // Even ACL-authenticated users must provide valid adapter key for AutoDJ operations
+         $authKey = $request->getHeaderLine('X-Liquidsoap-Api-Key');
+         $asAutoDj = !empty($authKey) && $station->validateAdapterApiKey($authKey);
      }
```

Both fixes should be applied. Fix 1 is the primary defense (defense in depth — this endpoint should never be publicly accessible). Fix 2 corrects the logic flaw so that `$asAutoDj` is only `true` when the adapter API key is actually valid, regardless of how authentication was performed.

## References
- https://github.com/AzuraCast/AzuraCast/security/advisories/GHSA-4fm3-ggg2-c6qx
- https://github.com/AzuraCast/AzuraCast/commit/13fa7a71435629147b351d3ee151b8de6acd5c8c
- https://github.com/AzuraCast/AzuraCast
