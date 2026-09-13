# [M] Denial of Service in mem

## Summary
Severity: Medium
Advisory: GHSA-4xcv-9jjx-gfj3
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-07-05
Source: https://github.com/advisories/GHSA-4xcv-9jjx-gfj3
Type: github-advisory

## Affected
- npm: `mem` — affected >=0 <4.0.0

## Details
Versions of `mem` prior to 4.0.0 are vulnerable to Denial of Service (DoS).  The package fails to remove old values from the cache even after a value passes its `maxAge` property. This may allow attackers to exhaust the system's memory if they are able to abuse the application logging.


## Recommendation

Upgrade to version 4.0.0 or later.

## References
- https://github.com/sindresorhus/mem/commit/da4e4398cb27b602de3bd55f746efa9b4a31702b
- https://bugzilla.redhat.com/show_bug.cgi?id=1623744
- https://snyk.io/vuln/npm:mem:20180117
- https://www.npmjs.com/advisories/1084
