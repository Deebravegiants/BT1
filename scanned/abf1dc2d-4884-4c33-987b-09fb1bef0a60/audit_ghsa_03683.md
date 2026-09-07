# [M] Insecure Default Configuration in tesseract.js

## Summary
Severity: Medium
Advisory: GHSA-83rx-c8cr-6j8q
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2019-06-05
Source: https://github.com/advisories/GHSA-83rx-c8cr-6j8q
Type: github-advisory

## Affected
- npm: `tesseract.js` — affected >=0 <1.0.19

## Details
Versions of `tesseract.js` prior to 1.0.19 default to using a third-party proxy.  Requests may be proxied through `crossorigin.me` which clearly states is not suitable for production use. This may lead to instability and privacy violations.


## Recommendation

Upgrade to version 1.0.19 or later.

## References
- https://github.com/naptha/tesseract.js/pull/267
- https://github.com/naptha/tesseract.js/commit/679eba055f2a4271558e86beec3d1b70cae3fb28
- https://snyk.io/vuln/SNYK-JS-TESSERACTJS-174085
- https://www.npmjs.com/advisories/792
