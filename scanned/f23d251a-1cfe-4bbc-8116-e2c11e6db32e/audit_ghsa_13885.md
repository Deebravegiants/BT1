# [H] is-http2 vulnerable to Improper Input Validation

## Summary
Severity: High
Advisory: GHSA-2275-rpf5-xv8h
CVE: CVE-2022-25906
CWE: CWE-20, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-01
Source: https://github.com/advisories/GHSA-2275-rpf5-xv8h
Type: github-advisory

## Affected
- npm: `is-http2` — affected >=0

## Details
All versions of the package is-http2 are vulnerable to Command Injection due to missing input sanitization or other checks, and sandboxes being employed to the isH2 function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25906
- https://github.com/stefanjudis/is-http2
- https://github.com/stefanjudis/is-http2/blob/master/index.js#L23
- https://github.com/stefanjudis/is-http2/blob/master/index.js%23L23
- https://security.snyk.io/vuln/SNYK-JS-ISHTTP2-3153878
