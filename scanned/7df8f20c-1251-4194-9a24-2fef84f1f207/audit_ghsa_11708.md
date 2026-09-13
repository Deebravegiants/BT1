# [M] AVideo has User Group-Based Category Access Control Bypass via Missing and Broken Group Filtering in categories.json.php

## Summary
Severity: Medium
Advisory: GHSA-73gr-r64q-7jh4
CVE: CVE-2026-34364
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-30
Source: https://github.com/advisories/GHSA-73gr-r64q-7jh4
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The `categories.json.php` endpoint, which serves the category listing API, fails to enforce user group-based access controls on categories. In the default request path (no `?user=` parameter), user group filtering is entirely skipped, exposing all non-private categories including those restricted to specific user groups. When the `?user=` parameter is supplied, a type confusion bug causes the filter to use the admin user's (user_id=1) group memberships instead of the current user's, rendering the filter ineffective.

## Details

The vulnerability has two related failures in `objects/categories.json.php` and `objects/category.php`:

**1. Default request — group filtering completely skipped**

In `categories.json.php:17-24`, when `$_GET['user']` is not set, `$sameUserGroupAsMe` defaults to `false`:

```php
// categories.json.php:17-24
$onlyWithVideos = false;
$sameUserGroupAsMe = false;
if(!empty($_GET['user'])){
    $onlyWithVideos = true;
    $sameUserGroupAsMe = true;
}
$categories = Category::getAllCategories(true, $onlyWithVideos, false, $sameUserGroupAsMe);
```

In `category.php:438-452`, the user group filter is gated on `$sameUserGroupAsMe` being truthy:

```php
// category.php:438-452
if ($sameUserGroupAsMe) {
    $users_groups = UserGroups::getUserGroups($sameUserGroupAsMe);
    $users_groups_id = array(0);
    foreach ($users_groups as $value) {
        $users_groups_id[] = $value['id'];
    }
    $sql .= " AND ("
        . "(SELECT count(*) FROM categories_has_users_groups chug WHERE c.id = chug.categories_id) = 0 OR "
        . "(SELECT count(*) FROM categories_has_users_groups chug2 WHERE c.id = chug2.categories_id AND users_groups_id IN (" . implode(',', $users_groups_id) . ")) >= 1 "
        . ")";
}
```

Since `$sameUserGroupAsMe = false`, the entire block is skipped. All non-private categories are returned regardless of their user group restrictions set via the `categories_has_users_groups` table.

**2. With `?user=` parameter — boolean-to-integer type confusion**

When `$_GET['user']` is non-empty, `$sameUserGroupAsMe` is set to boolean `true` (line 21). This value is passed to `UserGroups::getUserGroups($sameUserGroupAsMe)` at `category.php:440`.

In `userGroups.php:349-379`, the parameter is used as `$users_id`:

```php
// userGroups.php:349,371,379
public static function getUserGroups($users_id){
    // ...
    $sql = "SELECT uug.*, ug.* FROM users_groups ug"
            . " LEFT JOIN users_has_users_groups uug ON users_groups_id = ug.id WHERE users_id = ? ";
    // ...
    $res = sqlDAL::readSql($sql, "i", [$users_id]);
```

PHP casts boolean `true` to integer `1` for the prepared statement bind, resulting in `WHERE users_id = 1` — fetching the **admin user's** group memberships. The filter then allows categories visible to admin groups, effectively granting any unauthenticated user the admin's category visibility.

**3. getTotalCategories also unfiltered**

`getTotalCategories()` at `category.php:978` does not accept a `$sameUserGroupAsMe` parameter at all, so the total count always reflects the unfiltered category set.

The endpoint requires no authentication — it uses `allowOrigin()` (a CORS header helper) and is publicly routable via the `.htaccess` rewrite rule: `RewriteRule ^categories.json$ objects/categories.json.php`.

## PoC

```bash
# 1. Fetch all categories without authentication — no group filtering applied
curl -s 'https://target/categories.json' | jq '.rows[] | {id, name, private, users_groups_ids_array}'

# Returns ALL non-private categories including those restricted to specific user groups.
# The users_groups_ids_array field reveals which groups each category is restricted to.
# Categories with non-empty users_groups_ids_array should be hidden from users not in those groups.

# 2. Attempt the "filtered" path — still broken due to boolean->int cast
curl -s 'https://target/categories.json?user=1' | jq '.rows[] | {id, name, private, users_groups_ids_array}'

# This applies group filtering but uses admin's groups (users_id=1) instead of the
# current user's groups, so group-restricted categories visible to admin are exposed.
```

## Impact

Any unauthenticated user can:

- **Enumerate all non-private categories** regardless of user group restrictions, bypassing the intended access control model where categories are restricted to specific user groups via the CustomizeUser plugin's `categories_has_users_groups` table.
- **Discover the user group configuration** for each category via the `users_groups_ids_array` field in the response, revealing the internal access control structure.
- **Identify group-restricted content areas** that should be hidden, which could be used to target further access control bypasses on the videos within those categories.

The severity is Medium because this is an information disclosure of category metadata (names, descriptions, icons, group assignments) rather than the actual video content within restricted categories. However, the exposure of the access control structure itself (which groups have access to which categories) is a meaningful information leak.

## Recommended Fix

In `objects/categories.json.php`, pass the current user's ID (or 0 for unauthenticated users) instead of a boolean:

```php
// categories.json.php — replace lines 17-24
$onlyWithVideos = false;
$sameUserGroupAsMe = false;
if(!empty($_GET['user'])){
    $onlyWithVideos = true;
}
// Always apply user group filtering using the logged-in user's ID
$currentUserId = User::getId();
if (!empty($currentUserId)) {
    $sameUserGroupAsMe = $currentUserId;
} else {
    // For unauthenticated users, pass a value that will filter to only
    // categories with no group restrictions
    $sameUserGroupAsMe = -1; // Non-existent user ID, will match no groups
}

$categories = Category::getAllCategories(true, $onlyWithVideos, false, $sameUserGroupAsMe);
```

Additionally, in `category.php:getAllCategories()`, ensure the group filter block always runs when categories have group restrictions, not only when `$sameUserGroupAsMe` is truthy. A more robust approach:

```php
// category.php — replace the sameUserGroupAsMe block (lines 438-452)
// Always filter by user groups if any categories have group restrictions
$users_groups_id = array(0);
if ($sameUserGroupAsMe && $sameUserGroupAsMe > 0) {
    $users_groups = UserGroups::getUserGroups($sameUserGroupAsMe);
    foreach ($users_groups as $value) {
        $users_groups_id[] = $value['id'];
    }
}
$sql .= " AND ("
    . "(SELECT count(*) FROM categories_has_users_groups chug WHERE c.id = chug.categories_id) = 0 OR "
    . "(SELECT count(*) FROM categories_has_users_groups chug2 WHERE c.id = chug2.categories_id AND users_groups_id IN (" . implode(',', $users_groups_id) . ")) >= 1 "
    . ")";
```

This ensures that even when no user is logged in, categories with group restrictions are hidden (only categories with zero group restrictions are shown). The `getTotalCategories()` function should also be updated to accept and apply the same `$sameUserGroupAsMe` filter.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-73gr-r64q-7jh4
- https://nvd.nist.gov/vuln/detail/CVE-2026-34364
- https://github.com/WWBN/AVideo/commit/6e8a673eed07be5628d0b60fbfabd171f3ce74c9
- https://github.com/WWBN/AVideo
