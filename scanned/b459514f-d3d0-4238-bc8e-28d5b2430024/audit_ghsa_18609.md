# [M] rollbar vulnerable to Prototype Pollution in merge()

## Summary
Severity: Medium
Advisory: GHSA-xcg2-9pp4-j82x
CVE: CVE-2025-62517
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-xcg2-9pp4-j82x
Type: github-advisory

## Affected
- npm: `rollbar` — affected >=0 <2.26.5
- npm: `rollbar` — affected >=3.0.0-alpha1 <3.0.0-beta5

## Details
### Impact

Prototype pollution vulnerability in merge(). If application code calls `rollbar.configure()` with untrusted input, prototype pollution is possible.

### Patches

Fixed in 2.26.5 and 3.0.0-beta5.

### Workarounds

Ensure that values passed to `rollbar.configure()` do not contain untrusted input.

### References

Fixed in https://github.com/rollbar/rollbar.js/pull/1394 (2.26.x) and https://github.com/rollbar/rollbar.js/pull/1390 (3.x)

## References
- https://github.com/rollbar/rollbar.js/security/advisories/GHSA-xcg2-9pp4-j82x
- https://nvd.nist.gov/vuln/detail/CVE-2025-62517
- https://github.com/rollbar/rollbar.js/pull/1390
- https://github.com/rollbar/rollbar.js/pull/1394
- https://github.com/rollbar/rollbar.js/commit/61032fe6c208b71e249514800808a54bcb8cb8bb
- https://github.com/rollbar/rollbar.js/commit/d717def8b68f4a947975d0aebb729869cdb2d343
- https://github.com/rollbar/rollbar.js
