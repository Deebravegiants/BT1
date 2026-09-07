# [M] Open redirect in Slashify

## Summary
Severity: Medium
Advisory: GHSA-f4hq-453j-p95f
CVE: CVE-2021-3189
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-02-05
Source: https://github.com/advisories/GHSA-f4hq-453j-p95f
Type: github-advisory

## Affected
- npm: `slashify` — affected >=0

## Details
The package is an Express middleware that normalises routes by stripping any final slash, redirecting, for example, `bookings/latest/` to `bookings/latest`. However, it does not validate the path it redirects to in any way. In particular, if the path starts with two slashes (or two backslashes, or a slash and a backslash, etc.) it may redirect to a different domain.

Consider the [example from the docs](https://www.npmjs.com/package/slashify#usage). Assume we have run it and started a server on `localhost:3000`, then visiting `localhost:3000///github.com/` redirects you to https://github.com.

## Recommendation

This vulnerability is currently un-patched in the `slashify` package so there is no known safe version of this package. Discontinuing use of `slashify` is recommended.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3189
- https://github.com/divshot/slashify
- https://security.netapp.com/advisory/ntap-20210401-0004
- https://securitylab.github.com/advisories/GHSL-2020-199-open-redirect-slashify
- https://www.npmjs.com/package/slashify
