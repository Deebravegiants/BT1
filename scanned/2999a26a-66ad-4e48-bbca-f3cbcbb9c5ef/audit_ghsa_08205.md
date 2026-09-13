# [M] AVideo: Password Hash Leak in MobileManager OAuth Redirect URL Enables Account Takeover

## Summary
Severity: Medium
Advisory: GHSA-5w8w-26ch-v5cw
CVE: CVE-2026-43875
CWE: CWE-598
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-5w8w-26ch-v5cw
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

`plugin/MobileManager/oauth2.php` completes an OAuth login by sending an HTTP 302 `Location: oauth2Success.php?user=<email>&pass=<HASH>` where `<HASH>` is the victim's stored password hash (`md5(hash("whirlpool", sha1(password)))`) read directly from the `users` table. AVideo's own login endpoint (`objects/login.json.php`) accepts an `encodedPass=1` flag that bypasses hashing and performs a direct string comparison between the supplied value and the stored hash. Anyone who captures the redirect URL — via server logs, referrer leakage, or browser history — therefore obtains a credential equivalent to the plaintext password and can fully take over the account, including admin accounts.

## Details

### Sink: hash inlined in a GET redirect

`plugin/MobileManager/oauth2.php:98-102`:

```php
$pass = rand();
$users_id = User::createUserIfNotExists($user, $pass, $name, $email, $photoURL);
$adapter->disconnect();
$userObject = new User($users_id);
header("Location: oauth2Success.php?user=" . $userObject->getUser() . "&pass=" . $userObject->getPassword());
```

`$userObject->getPassword()` returns the raw database column (`objects/user.php:159-162`):

```php
public function getPassword()
{
    return strip_tags($this->password);
}
```

The returned value is the stored password hash for the account (existing or freshly-created). It is transported to the browser as a query-string parameter in the `Location:` header, so it is written to:

* Web-server access logs (`combined` / `main` log formats record the full request line including query string).
* Upstream proxy / CDN / WAF logs.
* Any error monitoring / APM that captures request URLs (Sentry, Datadog, New Relic defaults).
* The victim's browser history (persistent local artifact).
* The `Referer` header on subsequent navigation from the rendered `oauth2Success.php` page if the page or its assets load any external origin and the browser's `Referrer-Policy` is not strict.

### Hash equals plaintext for login

`objects/login.json.php:182-209`:

```php
if (!empty($_GET['user'])) {
    $_POST['user'] = $_GET['user'];
}
if (!empty($_GET['pass'])) {
    $_POST['pass'] = $_GET['pass'];
}
if (!empty($_GET['encodedPass'])) {
    $_POST['encodedPass'] = $_GET['encodedPass'];
}
...
$user = new User(0, $_POST['user'], $_POST['pass']);
...
$resp = $user->login(false, @$_POST['encodedPass']);
```

`objects/user.php:1272-1279` passes `$encodedPass` to `find()`:

```php
if (strtolower($encodedPass) === 'false') {
    $encodedPass = false;
}
...
$user = $this->find($this->user, $this->password, true, $encodedPass);
```

`objects/user.php:1785-1794`:

```php
if ($pass !== false) {
    if (!encryptPasswordVerify($pass, $result['password'], $encodedPass)) {
        ...
        return false;
    }
}
```

`objects/functions.php:2312-2331`:

```php
function encryptPasswordVerify(#[\SensitiveParameter] $password, $hash, $encodedPass = false)
{
    global $advancedCustom, $global;
    if (!$encodedPass || $encodedPass === 'false') {
        $passwordSalted  = encryptPassword($password);
        $passwordUnSalted = encryptPassword($password, true);
    } else {
        $passwordSalted  = $password;   // <- direct use, no hashing
        $passwordUnSalted = $password;
    }
    $isValid = $passwordSalted === $hash || $passwordUnSalted === $hash;
    ...
}
```

When `encodedPass` is truthy, the supplied value is compared as-is against the stored hash. The captured redirect parameter `pass=<HASH>` is therefore a valid login credential when replayed with `encodedPass=1`.

### Compounding factors

* The redirect is a raw `Location:` (GET), not a POST — the secret is placed in a URL which is by definition non-confidential transport.
* No CSRF token, no `state` parameter tied to the session, and no single-use token is used on `/plugin/MobileManager/oauth2.php`.
* `login.json.php` does not require a CSRF token or captcha on the first attempt (`checkLoginAttempts()` at `objects/user.php:1282` only rate-limits after failures, and the attacker succeeds on the first try).
* By contrast, the non-plugin flow in `objects/login.json.php:144-145` already sets session state server-side (`$userObject->login(true)`), demonstrating the project already has a safer pattern available.

## PoC

Prerequisites: `MobileManager` plugin enabled and at least one supported login provider (e.g. `LoginGoogle`) configured with valid keys — both are common production settings for this product.

1. Victim initiates the mobile OAuth flow:

   ```
   GET /plugin/MobileManager/oauth2.php?type=Google
   ```

2. After the victim authorizes at the provider, the server sends:

   ```
   HTTP/1.1 302 Found
   Location: oauth2Success.php?user=victim%40example.com&pass=9d7ab4...stored-hash...
   ```

   This request-line — including the password hash — is written to the web server's access log (default `combined` format) and to any upstream proxy/CDN log. It also appears in the victim's browser history.

3. Attacker obtains `<HASH>` from any of those channels.

4. Attacker logs in as the victim without knowing the plaintext password:

   ```
   curl -i -c cookies.txt \
     'https://target.example.com/objects/login.json.php?user=victim@example.com&pass=<HASH>&encodedPass=1'
   ```

   Expected response: `200 OK` with JSON containing `id`, `user`, `PHPSESSID`, `isAdmin`, `email`, and a `Set-Cookie: PHPSESSID=...` that grants full account access. The attacker can now browse, upload, modify the victim's channel, or — if the victim is an admin — access `/mvideos` and all admin endpoints.

## Impact

* Full account takeover of any user who has ever logged in through the MobileManager OAuth endpoint.
* If the victim is an administrator, the attacker gains administrative control of the AVideo instance (user management, plugin config, site-wide content).
* The exposed hash works indefinitely: it remains valid for as long as the victim does not change their password, so a one-time log/history/referrer capture yields a persistent credential.
* Passes silently — from the application's perspective, the attacker is just a legitimate login with `encodedPass=1` (a flag the product itself uses for mobile-app "remember me" flows).

## Recommended Fix

1. Never place the password hash (or any credential-equivalent material) in a URL. In `plugin/MobileManager/oauth2.php`, mirror what `objects/login.json.php:143-146` already does for the web flow — establish the session server-side and redirect to a URL with no credentials:

   ```php
   $userObject = new User(0, $user, $pass);
   $userObject->login(true);   // server-side session
   header("Location: oauth2Success.php");
   ```

2. Additionally, remove or hard-restrict the `encodedPass` branch in `objects/functions.php:2319-2329`. If a "hash-equivalent" credential must exist for the mobile app, replace it with a short-lived, single-use, server-issued bearer token bound to the session, rather than the persistent database hash.

3. Add a `state` parameter and CSRF protection on `/plugin/MobileManager/oauth2.php` so the redirect cannot be initiated from a third-party origin.

4. For defense-in-depth, strip query strings containing `pass=` from access-log formats and ensure `oauth2Success.php` sets `Referrer-Policy: no-referrer` while it is being deprecated.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-5w8w-26ch-v5cw
- https://nvd.nist.gov/vuln/detail/CVE-2026-43875
- https://github.com/WWBN/AVideo/commit/977cd6930a97571a26da4239e25c8096dd4ecbc1
- https://github.com/WWBN/AVideo
