# [M] Server-Side Request Forgery in link-preview-js

## Summary
Severity: Medium
Advisory: GHSA-h9cw-7g8j-h66h
CVE: CVE-2022-25876
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-02
Source: https://github.com/advisories/GHSA-h9cw-7g8j-h66h
Type: github-advisory

## Affected
- npm: `link-preview-js` — affected >=0 <2.1.17

## Details
The package link-preview-js before 2.1.17 are vulnerable to Server-side Request Forgery (SSRF) which allows attackers to send arbitrary requests to the local network and read the response. This is due to flawed DNS rebinding protection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25876
- https://github.com/ospfranco/link-preview-js/issues/115
- https://github.com/ospfranco/link-preview-js/pull/117
- https://github.com/ospfranco/link-preview-js
- https://snyk.io/vuln/SNYK-JS-LINKPREVIEWJS-2933520
