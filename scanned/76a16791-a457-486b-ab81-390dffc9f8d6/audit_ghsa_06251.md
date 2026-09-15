# [M] Winter: CSRF through AJAX handler names reachable as backend page actions

## Summary
Severity: Medium
Advisory: GHSA-p2ch-c2c3-4xm5
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-p2ch-c2c3-4xm5
Type: github-advisory

## Affected
- Packagist: `winter/wn-backend-module` — affected >=1.0.319 <1.2.14

## Details
### Impact

Affected versions of Winter CMS allow a backend AJAX handler to be invoked by a plain top-level `GET` navigation with no CSRF token. `Backend\Classes\Controller::actionExists()` accepted any public method on a controller as a page action, so handler-shaped names were never reserved from URL dispatch: an authenticated and authorized request to `/backend/system/eventlogs/index_onEmptyLog` reached the handler of the same name and truncated the system event log. Backend paths are routed through `Route::any`, and CSRF validation is skipped for `HEAD`, `GET` and `OPTIONS` requests.

The default `SameSite=Lax` session cookie is sent on top-level cross-site navigation, so a link on an attacker-controlled page is sufficient — no form, no script and no token. Handler arguments are taken from URL path segments, so the attacker also chooses the target record. Affected handlers across the `backend`, `cms` and `system` modules cover log truncation, resetting settings to their defaults, altering backend user state, and deleting CMS templates. None of them disclose data to the attacker or write attacker-controlled content, so the impact is destructive and state-changing rather than confidential.

To actively exploit this issue, an attacker would need no account of their own, but would need an authenticated backend user holding the relevant permission to follow an attacker-supplied link. The permissions guarding the affected handlers, `system.access_logs` included, are by default assigned only to the built-in Developer role.

### Patches

Page-action dispatch is now restricted to all-lowercase method names, which reserves handler-shaped names (`onFoo`, `index_onFoo`) from being reached by URL. AJAX dispatch is unchanged: handlers continue to work over `POST` with the `X-WINTER-REQUEST-HANDLER` header exactly as before, and need no changes.

>**IMPORTANT:** **This fix includes a breaking change to backend action routing.** A public controller method used as a page action must now be named in lowercase — `coming_soon()` rather than `comingSoon()` — and dashed URLs are normalised to `snake_case`, so `/coming-soon` now resolves to `coming_soon()` instead of `comingSoon()`. Plugins with a camelCase page action should rename the method and its view file to match; the published URL does not need to change. Core is unaffected, and a survey of the plugin ecosystem found the change affects only a small number of plugins.

This security issue has been fixed in [v1.2.14](https://github.com/wintercms/winter/commit/353b23804dee2acf49fca996c72637040446824f).

### Workarounds

If you cannot upgrade, apply https://github.com/wintercms/winter/commit/353b23804dee2acf49fca996c72637040446824f manually.

As an interim mitigation, set `'same_site' => 'strict'` in `config/session.php`. A strict session cookie is not sent on cross-site top-level navigation, which prevents the victim's session accompanying an attacker's link. Review this against any single sign-on or inbound-link flows into your backend first, as it also affects legitimate cross-site entry.

### References

Credit to Awwader ([@NRAwwad](https://github.com/NRAwwad)) for reporting the issue.

### For more information

If you have any questions or comments about this advisory:
- Email us at [hello@wintercms.com](mailto:hello@wintercms.com)

## References
- https://github.com/wintercms/winter/security/advisories/GHSA-p2ch-c2c3-4xm5
- https://github.com/wintercms/winter/commit/353b23804dee2acf49fca996c72637040446824f
- https://github.com/wintercms/winter
- https://github.com/wintercms/winter/releases/tag/v1.2.14
