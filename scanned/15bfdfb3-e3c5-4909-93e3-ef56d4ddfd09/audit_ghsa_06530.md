# [M] Tornado vulnerable to Header Injection and XSS via reason argument

## Summary
Severity: Medium
Advisory: GHSA-pr2v-jx2c-wg9f
CVE: CVE-2025-67724
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-20
Source: https://github.com/advisories/GHSA-pr2v-jx2c-wg9f
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.3

## Details
# Header injection and XSS via `reason` argument

## Summary

The `reason` argument (used by both `RequestHandler.set_status` and `tornado.web.HTTPError` is designed to allow applications to pass custom "reason" phrases (the "Not Found" in `HTTP/1.1 404 Not Found`) to the HTTP status line (mainly for non-standard status codes). Vulnerabilities exist in Tornado versions prior to 6.5.3 if untrusted data is passed as the `reason` argument.

## Details

In vulnerable versions, the supplied `reason` phrase is used unescaped in HTTP headers (where it could be used for header injection) or in HTML in the default error page (where it could be used for XSS).

## Impact

* **Type:** Reflected Cross-Site Scripting (CWE-79) in default error page, or header injection (CWE-644)
* **Actors:** Remote attacker who can cause the application to raise `HTTPError`/`set_status` with an attacker-controlled `reason` (e.g., via query parameter used by developer).
* **Effect:** Execution of arbitrary JavaScript in victims' browsers when they view the error page — possible session token theft, CSRF escalation, UI spoofing, or other client-side attacks depending on context.
* **Scope:** Only applications that explicitly reflect untrusted input into `reason` are affected.

## Mitigation

Aside from upgrading to Tornado 6.5.3 or newer, the vulnerability can be mitigated by not using untrusted data for the `reason` argument. In the intended use case the `reason` argument would generally be a string literal and not derived from user input. Also, the `reason` argument is rarely required (reason phrases are not used at all in HTTP/2) and can generally be omitted.

For a general-purpose error message in HTTPError, consider using the `log_message` argument instead of `reason`.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-pr2v-jx2c-wg9f
- https://nvd.nist.gov/vuln/detail/CVE-2025-67724
- https://github.com/tornadoweb/tornado/commit/9c163aebeaad9e6e7d28bac1f33580eb00b0e421
- https://github.com/pypa/advisory-database/tree/main/vulns/tornado/PYSEC-2025-265.yaml
- https://github.com/tornadoweb/tornado
- https://github.com/tornadoweb/tornado/releases/tag/v6.5.3
