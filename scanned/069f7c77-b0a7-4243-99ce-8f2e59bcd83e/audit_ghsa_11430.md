# [C] parse-server has cloud function validator bypass via prototype chain traversal

## Summary
Severity: Critical
Advisory: GHSA-vpj2-qq7w-5qq6
CVE: CVE-2026-34532
CWE: CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-vpj2-qq7w-5qq6
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.7.0-alpha.11
- npm: `parse-server` — affected >=0 <8.6.67

## Details
### Impact

An attacker can bypass Cloud Function validator access controls by appending `.prototype.constructor` to the function name in the URL. When a Cloud Function handler is declared using the `function` keyword and its validator is a plain object or arrow function, the trigger store traversal resolves the handler through its own prototype chain while the validator store fails to mirror this traversal, causing all access control enforcement to be skipped.

This allows unauthenticated callers to invoke Cloud Functions that are meant to be protected by validators such as `requireUser`, `requireMaster`, or custom validation logic.

### Patches

The trigger store traversal now verifies that each intermediate node is a legitimate store object before continuing traversal. If the traversal encounters a non-store value such as a function handler, it stops and returns an empty store, preventing prototype chain escape.

### Workarounds

Use arrow functions instead of the `function` keyword for Cloud Function handlers. Arrow functions do not have a `prototype` property and are not affected by this vulnerability.

### Resources

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-vpj2-qq7w-5qq6
- Fix Parse Server 9: https://github.com/parse-community/parse-server/pull/10342
- Fix Parse Server 8: https://github.com/parse-community/parse-server/pull/10343

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-vpj2-qq7w-5qq6
- https://nvd.nist.gov/vuln/detail/CVE-2026-34532
- https://github.com/parse-community/parse-server/pull/10342
- https://github.com/parse-community/parse-server/pull/10343
- https://github.com/parse-community/parse-server/commit/4fc48cf28f22eea200d74d883505f485234a48d7
- https://github.com/parse-community/parse-server/commit/dc59e272665644083c5b7f6862d88ce1ef0b2674
- https://github.com/parse-community/parse-server
