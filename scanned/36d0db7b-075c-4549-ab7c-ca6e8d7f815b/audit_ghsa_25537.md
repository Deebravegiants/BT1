# [M] Cross-site Scripting in fullpage.js

## Summary
Severity: Medium
Advisory: GHSA-h3cq-j957-vhxg
CVE: CVE-2022-1330
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-h3cq-j957-vhxg
Type: github-advisory

## Affected
- npm: `fullpage.js` — affected >=0 <4.0.5

## Details
using fullpage.js you can create a anchor tag . But when put href in anchor then it does not sanitize the url which allow for a break in the context of anchor element and can add our new element.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1330
- https://github.com/alvarotrigo/fullPage.js/pull/4360
- https://github.com/alvarotrigo/fullpage.js/commit/e7a5db42711700c8a584e61b5e532a64039fe92b
- https://github.com/alvarotrigo/fullpage.js
- https://huntr.dev/bounties/08d2a6d0-772f-4b05-834e-86343f263c35
