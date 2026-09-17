# [M] parse-server: Malformed `$regex` query leaks database error details in API response

## Summary
Severity: Medium
Advisory: GHSA-9cp7-3q5w-j92g
CVE: CVE-2026-30835
CWE: CWE-209
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-06
Source: https://github.com/advisories/GHSA-9cp7-3q5w-j92g
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.5.0-alpha.6
- npm: `parse-server` — affected >=0 <8.6.7

## Details
### Impact

A malformed $regex query parameter (e.g. `[abc)` causes the database to return a structured error object that is passed unsanitized through the API response. This leaks database internals such as error messages, error codes, code names, cluster timestamps, and topology details. The vulnerability is exploitable by any client that can send query requests, depending on the deployment's permission configuration.

### Patches

The fix sanitizes database error objects so that only a generic `"An internal server error occurred"` message is returned to clients, while the detailed error is logged server-side. The fix respects the `enableSanitizedErrorResponse` server option.

### Workarounds

There is no workaround other than upgrading. The error leakage occurs in the query execution layer and cannot be mitigated through server configuration or client-side changes.

### Resources

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-9cp7-3q5w-j92g
- Fix in Parse Server 9: https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.6
- Fix in Parse Server 8: https://github.com/parse-community/parse-server/releases/tag/8.6.7

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-9cp7-3q5w-j92g
- https://nvd.nist.gov/vuln/detail/CVE-2026-30835
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/8.6.7
- https://github.com/parse-community/parse-server/releases/tag/9.5.0-alpha.6
