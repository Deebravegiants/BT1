# [H] Open Redirect in ecstatic

## Summary
Severity: High
Advisory: GHSA-9q64-mpxx-87fg
CWE: CWE-601
Ecosystem: npm
Published: 2020-04-01
Source: https://github.com/advisories/GHSA-9q64-mpxx-87fg
Type: github-advisory

## Affected
- npm: `ecstatic` — affected >=0 <2.2.2
- npm: `ecstatic` — affected >=3.0.0 <3.3.2
- npm: `ecstatic` — affected >=4.0.0 <4.1.2

## Details
Versions of `ecstatic` prior to 4.1.2, 3.3.2 or 2.2.2 are vulnerable to Open Redirect. The package fails to validate redirects, allowing attackers to craft requests that result in an `HTTP 301` redirect to any other domains.


## Recommendation

If using `ecstatic` 4.x, upgrade to 4.1.2 or later.
If using `ecstatic` 3.x, upgrade to 3.3.2 or later.
If using `ecstatic` 2.x, upgrade to 2.2.2 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10775
- https://www.npmjs.com/advisories/830
