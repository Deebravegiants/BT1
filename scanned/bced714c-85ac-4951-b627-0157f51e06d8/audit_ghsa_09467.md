# [M] phpMyFAQ has an Authorization Bypass in All Admin Pages Due to Non-Terminating Permission Check

## Summary
Severity: Medium
Advisory: GHSA-hpgw-ww76-c68r
CVE: CVE-2026-46362
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-hpgw-ww76-c68r
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

`AbstractAdministrationController::userHasPermission()` catches the `ForbiddenException` thrown when a user lacks a specific permission, sends a "forbidden" HTML page via `$response->send()`, but does not terminate execution. The calling controller method continues to execute, fetches protected data, renders the full template, and returns it as a Response. The final `$response->send()` in `admin/index.php` outputs the protected page content after the forbidden page, leaking all permission-protected admin data to any authenticated admin user regardless of their actual permissions.

## Details

The parent class `AbstractController::userHasPermission()` (`phpmyfaq/src/phpMyFAQ/Controller/AbstractController.php:317-327`) correctly enforces authorization by throwing a `ForbiddenException` when the user lacks the required permission. This exception would normally propagate to Symfony's HttpKernel exception handler, which would return an error response and prevent the controller from continuing.

However, `AbstractAdministrationController` overrides this method at line 390-399:

```php
#[\Override]
protected function userHasPermission(PermissionType $permissionType): void
{
    try {
        parent::userHasPermission($permissionType);
    } catch (ForbiddenException $exception) {
        $response = $this->getForbiddenPage($exception->getMessage());
        $response->send();  // Outputs HTML but does NOT terminate execution
    } catch (Exception $exception) {
        $this->configuration->getLogger()->error($exception->getMessage());
        // Only logs, no response, no termination
    }
}
```

The critical flaw: after `$response->send()` at line 396, there is no `exit()`, `die()`, `return`, or re-throw. PHP execution continues normally into the calling controller method.

For example, in `AdminLogController::index()` (`phpmyfaq/src/phpMyFAQ/Controller/Administration/AdminLogController.php:45-83`):

```php
public function index(Request $request): Response
{
    $this->userHasPermission(PermissionType::STATISTICS_ADMINLOG);
    // ^^^ If user lacks permission: forbidden page is echoed, but execution continues

    // ... all of this still executes:
    $loggingData = $this->adminLog->getAll();  // Fetches ALL admin log entries
    // ...
    return $this->render('@admin/statistics/admin-log.twig', [
        // ... full admin log data including IPs, usernames, actions
        'loggingData' => $currentItems,
    ]);
}
```

The entry point `admin/index.php` then calls `$response->send()` on the returned Response, appending the full protected page to the already-sent forbidden page in the HTTP response body.

The second `catch` block (line 397-398) for generic `Exception` is even worse — it only logs the error without sending any response or terminating, so the protected page renders with no forbidden notice at all.

**58 admin controllers** extend `AbstractAdministrationController` and call `userHasPermission()`, meaning every permission-protected admin page is affected. This includes:
- Admin logs (user IPs, actions, usernames)
- User management (user data, permissions)
- System information (server configuration, PHP info)
- Configuration pages (all application settings)
- Backup pages
- All other admin functionality

## PoC

1. Create a test admin user with minimal permissions (e.g., only FAQ editing, no statistics access):

2. Authenticate as the limited admin user and request a permission-protected page:

```bash
# Get admin session cookies by logging in
curl -c cookies.txt -d 'faqusername=limited_admin&faqpassword=password&pmf-csrf-token=TOKEN' \
  'https://TARGET/admin/?action=login'

# Access admin log page (requires STATISTICS_ADMINLOG permission)
curl -b cookies.txt -s 'https://TARGET/admin/statistics/admin-log' | tee response.html

# The response contains BOTH the forbidden page HTML AND the full admin log:
grep -c 'You are not allowed' response.html    # 1 — forbidden page was sent
grep -c 'loggingData\|ad_adminlog_ip' response.html  # matches — admin log data also present

# Access system information (requires CONFIGURATION_EDIT permission)  
curl -b cookies.txt -s 'https://TARGET/admin/system-information' | tee sysinfo.html
# Contains PHP version, extensions, database info, server configuration
```

3. The HTTP response body contains the forbidden page HTML followed by the full protected page HTML, including all sensitive data.

## Impact

Any authenticated admin user — even one with zero administrative permissions beyond basic login — can access **every** permission-protected admin page by simply requesting its URL. The permission check sends a forbidden page but does not stop execution, so the protected content is always appended to the response.

Exposed data includes:
- **Admin logs**: All admin users' IP addresses, actions, and timestamps
- **User management**: User accounts, email addresses, permissions
- **System information**: PHP configuration, database details, server paths
- **Configuration**: All application settings including security-sensitive values
- **Backups**: Database export functionality

This effectively renders the entire admin permission system non-functional for the 58 page controllers using `AbstractAdministrationController`.

## Recommended Fix

Add `return` after sending the forbidden response, and re-throw for the generic Exception case:

```php
#[\Override]
protected function userHasPermission(PermissionType $permissionType): void
{
    try {
        parent::userHasPermission($permissionType);
    } catch (ForbiddenException $exception) {
        $response = $this->getForbiddenPage($exception->getMessage());
        $response->send();
        exit;  // Terminate execution to prevent controller from continuing
    } catch (Exception $exception) {
        $this->configuration->getLogger()->error($exception->getMessage());
        throw $exception;  // Re-throw to prevent controller from continuing
    }
}
```

A cleaner architectural fix would be to not swallow the exception at all, and instead let it propagate to the Symfony HttpKernel exception handler (which already handles `ForbiddenException` via `WebExceptionListener`):

```php
#[\Override]
protected function userHasPermission(PermissionType $permissionType): void
{
    // Simply delegate to parent — let ForbiddenException propagate
    // to the WebExceptionListener which renders the appropriate error page
    parent::userHasPermission($permissionType);
}
```

Or remove the override entirely, since the `WebExceptionListener` registered in the Kernel already handles exception-to-response conversion.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-hpgw-ww76-c68r
- https://nvd.nist.gov/vuln/detail/CVE-2026-46362
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-authorization-bypass-in-admin-pages-via-non-terminating-permission-check
