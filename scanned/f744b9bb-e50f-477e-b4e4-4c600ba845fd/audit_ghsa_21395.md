# [M] Cross site scripting in Metro UI

## Summary
Severity: Medium
Advisory: GHSA-633r-r4p8-pw3w
CVE: CVE-2022-41376
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-10-11
Source: https://github.com/advisories/GHSA-633r-r4p8-pw3w
Type: github-advisory

## Affected
- npm: `metro4` — affected >=4.4.0

## Details
Metro UI v4.4.0 to v4.5.1 was discovered to contain a reflected cross-site scripting (XSS) vulnerability via the Javascript function. User input is not properly sanitized before rendering in the `textarea` component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41376
- https://alicangonullu.org/konu/138
- https://github.com/olton/Metro-UI-CSS
- https://youtu.be/_wzGVpX54Rc
