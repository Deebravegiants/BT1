# [H] Valtimo has sensitive data exposure through HTTP request/response logging in LoggingRestClientCustomizer

## Summary
Severity: High
Advisory: GHSA-3jh5-rr2q-xfv7
CVE: CVE-2026-44516
CWE: CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-3jh5-rr2q-xfv7
Type: github-advisory

## Affected
- Maven: `com.ritense.valtimo:web` — affected >=12.4.0 <12.33.0
- Maven: `com.ritense.valtimo:web` — affected >=13.0.0 <13.26.0

## Details
### Summary

The `LoggingRestClientCustomizer` in the `web` module automatically intercepts all outgoing HTTP calls made via Spring's `RestClient` and logs the full request body, response body, and response headers. When an error response is received, this information is included in the thrown `HttpClientErrorException` message, which is logged at ERROR level by Spring's default exception handling — regardless of the application's DEBUG log level setting.

### Impact

The logged data can contain highly sensitive information including:
- Authentication credentials (JWT tokens, API keys, OAuth tokens) in request bodies or response headers
- Personal data (BSN, email addresses, case details) in request/response bodies
- Session tokens in `Set-Cookie` response headers

This data is exposed to:
- Anyone with access to application logs (stdout/log files)
- Users with access to logging aggregation tools (e.g. Grafana/Loki)
- Any Valtimo user with the admin role, through the built-in logging module (since Valtimo 12.5.0)

Leaked authentication credentials could be used to impersonate the Valtimo application against the target external API (e.g. ZGW services), compromising that API's security boundary.

Related: GHSA-hfrg-mcvw-8mch (similar sensitive data exposure in InboxHandlingService)

### Affected Code

`com.ritense.valtimo.web.logging.LoggingRestClientCustomizer#intercept` in the `web` module.

### Patched Versions

The vulnerability is fixed in:
- **12.33.0** (v12 release line) — see PR #600
- **13.26.0** (v13 release line) — see PR #599

The fix removes the request/response report, headers, and response body from the `HttpClientErrorException` constructor; only the HTTP status code and status text remain. The full request/response report is still emitted at DEBUG level (disabled in production).

### Mitigation

If you cannot upgrade to a patched version immediately, consider:
- Restricting access to application logs and the Valtimo logging module
- Adjusting the log level for `com.ritense.valtimo.web.logging` to WARN or higher (note: this only mitigates the DEBUG logging path; error responses still leak data via the exception message)

## References
- https://github.com/valtimo-platform/valtimo/security/advisories/GHSA-3jh5-rr2q-xfv7
- https://nvd.nist.gov/vuln/detail/CVE-2026-44516
- https://github.com/valtimo-platform/valtimo/pull/599
- https://github.com/valtimo-platform/valtimo/pull/600
- https://github.com/valtimo-platform/valtimo
