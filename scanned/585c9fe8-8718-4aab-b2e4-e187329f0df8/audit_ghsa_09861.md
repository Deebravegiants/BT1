# [H] Parser Server's streaming file download bypasses afterFind file trigger authorization

## Summary
Severity: High
Advisory: GHSA-hpm8-9qx6-jvwv
CVE: CVE-2026-34784
CWE: CWE-285
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-01
Source: https://github.com/advisories/GHSA-hpm8-9qx6-jvwv
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=9.0.0 <9.7.1-alpha.1
- npm: `parse-server` — affected >=0 <8.6.71

## Details
### Impact

File downloads via HTTP Range requests bypass the `afterFind(Parse.File)` trigger and its validators on storage adapters that support streaming (e.g. the default GridFS adapter). This allows access to files that should be protected by `afterFind` trigger authorization logic or built-in validators such as `requireUser`.

### Patches

The streaming file download path now executes the `afterFind(Parse.File)` trigger before sending any data. Authentication is resolved from the session token header so that trigger validators can distinguish authenticated from unauthenticated requests.

### Workarounds

Use `beforeFind(Parse.File)` instead of `afterFind(Parse.File)` for file access authorization. The `beforeFind` trigger runs on all download paths including streaming.

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-hpm8-9qx6-jvwv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34784
- https://github.com/parse-community/parse-server/pull/10361
- https://github.com/parse-community/parse-server/pull/10362
- https://github.com/parse-community/parse-server/commit/053109b3ee71815bc39ed84116c108ff9edbf337
- https://github.com/parse-community/parse-server/commit/a0b0c69fc44f87f80d793d257344e7dcbf676e22
- https://github.com/parse-community/parse-server
