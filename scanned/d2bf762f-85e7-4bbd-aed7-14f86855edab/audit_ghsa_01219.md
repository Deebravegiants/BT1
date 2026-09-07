# [H] DOM-based XSS in gmail-js

## Summary
Severity: High
Advisory: GHSA-c7pp-g2v2-2766
CVE: CVE-2016-1000228
CWE: CWE-79
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-c7pp-g2v2-2766
Type: github-advisory

## Affected
- npm: `gmail-js` — affected >=0 <0.6.5

## Details
Affected versions of `gmail-js` are vulnerable to cross-site scripting in the `tools.parse_response`, `helper.get.visible_emails_post`, and `helper.get.email_data_post` functions, which pass user input directly into the Function constructor.



## Recommendation

Update to version 0.6.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-1000228
- https://github.com/KartikTalwar/gmail.js/issues/281
- https://github.com/KartikTalwar/gmail.js/commit/a83436f499f9c01b04280af945a5a81137b6baf1
- https://github.com/KartikTalwar/gmail.js
- https://www.npmjs.com/advisories/125
