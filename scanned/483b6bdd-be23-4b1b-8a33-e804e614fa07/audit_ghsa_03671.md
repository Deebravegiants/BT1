# [M] Regular Expression Denial of Service in underscore.string

## Summary
Severity: Medium
Advisory: GHSA-v2p6-4mp7-3r9v
CWE: CWE-400
Ecosystem: npm
Published: 2019-06-14
Source: https://github.com/advisories/GHSA-v2p6-4mp7-3r9v
Type: github-advisory

## Affected
- npm: `underscore.string` — affected >=0 <3.3.5

## Details
Versions of `underscore.string` prior to *3.3.5* are vulnerable to Regular Expression Denial of Service (ReDoS).

The function `unescapeHTML` is vulnerable to ReDoS due to an overly-broad regex. The slowdown is approximately 2s for 50,000 characters but grows exponentially with larger inputs.


## Recommendation

Upgrade to version 3.3.5 or higher.

## References
- https://github.com/epeli/underscore.string/issues/510
- https://github.com/epeli/underscore.string/pull/517
- https://github.com/epeli/underscore.string/commit/f486cd684c94c12db48b45d52b1472a1b9661029
- https://www.npmjs.com/advisories/745
