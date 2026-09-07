# [M] Open Redirect in urijs

## Summary
Severity: Medium
Advisory: GHSA-8h2f-7jc4-7m3m
CVE: CVE-2022-0868
CWE: CWE-601
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-03-07
Source: https://github.com/advisories/GHSA-8h2f-7jc4-7m3m
Type: github-advisory

## Affected
- npm: `urijs` — affected >=0 <1.19.10

## Details
urijs prior to version 1.19.10 is vulnerable to open redirect. This is the result of a bypass for the fix to CVE-2022-0613.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0868
- https://github.com/medialize/uri.js/commit/a8166fe02f3af6dc1b2b888dcbb807155aad9509
- https://github.com/medialize/URI.js/releases/tag/v1.19.10
- https://github.com/medialize/uri.js
- https://huntr.dev/bounties/5f4db013-64bd-4a6b-9dad-870c296b0b02
