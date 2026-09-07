# [H] Winter: Authenticated backend users can bypass Users controller permission checks

## Summary
Severity: High
Advisory: GHSA-j5jq-cr68-v2xx
CVE: CVE-2026-35445
CWE: CWE-285, CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:L/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2026-08-12
Source: https://github.com/advisories/GHSA-j5jq-cr68-v2xx
Type: github-advisory

## Affected
- Packagist: `winter/wn-backend-module` — affected >=0 <1.2.13

## Details
### Impact

Affected versions of Winter CMS did not validate the handler name submitted through the form postback mechanism (`_handler` POST field) in the same way as AJAX requests (`X_WINTER_REQUEST_HANDLER` header). The AJAX path validates that handler names match the `on[A-Z][\w+]*` pattern, but the postback path passed the handler name directly to the handler dispatcher with no validation.

This allowed an authenticated backend user to call any method on a controller — including action-prefixed, protected, and private methods — by submitting a crafted POST request with a `_handler` field, as long as the controller either:

- Contains a publicly available action via the `$publicActions` property, or
- Degrades or removes the `$requiredPermissions` check in its constructor based on a condition

The backend's own Users controller was affected by the second scenario: it set `$requiredPermissions` to `null` for the `myaccount` action, allowing any authenticated backend user to access the controller without the `backend.manage_users` permission. Combined with the postback bypass, this allowed calling controller methods such as `update_onDelete`, `update_onRestore`, `update_onUnsuspendUser`, and `update_onManualPasswordReset` with attacker-controlled parameters.

Note that CSRF tokens are still verified on all POST requests, so the attacker must be logged into the backend with a valid session.

To actively exploit this security issue, an attacker would need access to the Backend with a user account with any level of access.

The Winter CMS maintainers strongly recommend that all Winter CMS sites that have any reliance on the roles & permissions system to update immediately. Security fixes have been backported to all major versions of Winter (1.0, 1.1, and 1.2).

### Patches

The postback handler path now validates handler names using the same rules as the AJAX path. The My Account functionality has been moved to a dedicated controller that does not expose user management methods. Defence in depth has been applied at the model level to prevent unauthorized user record modifications regardless of the entry point.

This security issue has been fixed as of v1.2.13.

### Workarounds

If users cannot upgrade, they may apply the following changes to their Winter CMS installation manually to resolve this issue:

1. In `modules/backend/classes/Controller.php`, validate the `_handler` POST field against the `on[A-Z][\w+]*` pattern before passing it to `runAjaxHandler()`.
2. In `modules/backend/controllers/Users.php`, remove the conditional that sets `$requiredPermissions` to `null` for the `myaccount` action.

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-j5jq-cr68-v2xx
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.13
