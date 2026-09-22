# [M] @hapi/inert has a static-file confinement bypass via sibling-prefix path

## Summary
Severity: Medium
Advisory: GHSA-rcvq-m9j9-6f4g
CVE: CVE-2026-48049
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-rcvq-m9j9-6f4g
Type: github-advisory

## Affected
- npm: `@hapi/inert` — affected >=4.0.0 <7.1.1

## Details
### Impact
`@hapi/inert` serves static files from a directory configured with `path` (in the `directory` / `file` handlers) or `relativeTo` (for `h.file()`), with confinement enforced by the `confine` option (default `true`). Before the patch, the confinement check compared the resolved absolute path against the confine directory using a raw string-prefix test, so a sibling directory whose absolute path begins with the same characters as the confine directory (eg. `/app/static-secret` next to a served `/app/static`) was incorrectly accepted as confined. An unauthenticated remote attacker who knows or guesses such a sibling name can read any file inside it via a request like `/..%2fstatic-secret/secret.txt`, provided the file is readable by the server process. Only applications that happen to have a sibling directory sharing a string prefix with the served directory are exploitable; applications with no such sibling are unaffected.

### Patches
Upgrade to 7.1.1.

### Workarounds
For users who cannot upgrade immediately: ensure the directory served via inert has no sibling whose name starts with the same characters (for example, rename `static-secret/` to `secret/`, or move it to a different parent directory).

### Resources
Pull Request: https://github.com/hapijs/inert/pull/176

## References
- https://github.com/hapijs/inert/security/advisories/GHSA-rcvq-m9j9-6f4g
- https://github.com/hapijs/inert/pull/176
- https://github.com/hapijs/inert/commit/a65e5b271b5c3405af463469959c5e052eb23a62
- https://github.com/hapijs/inert
