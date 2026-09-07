# [M] Cross-site Scripting in docsify

## Summary
Severity: Medium
Advisory: GHSA-qpqh-46qj-vwcw
CVE: CVE-2020-7680
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2021-05-18
Source: https://github.com/advisories/GHSA-qpqh-46qj-vwcw
Type: github-advisory

## Affected
- npm: `docsify` — affected >=0 <4.11.4

## Details
docsify prior to 4.11.4 is susceptible to Cross-site Scripting (XSS). Docsify.js uses fragment identifiers (parameters after # sign) to load resources from server-side .md files. Due to lack of validation here, it is possible to provide external URLs after the /#/ (domain.com/#//attacker.com) and render arbitrary JavaScript/HTML inside docsify page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7680
- https://github.com/docsifyjs/docsify/issues/1126
- https://github.com/docsifyjs/docsify/pull/1128
- https://snyk.io/vuln/SNYK-JS-DOCSIFY-567099
- http://packetstormsecurity.com/files/158515/Docsify.js-4.11.4-Cross-Site-Scripting.html
- http://packetstormsecurity.com/files/161495/docsify-4.11.6-Cross-Site-Scripting.html
- http://seclists.org/fulldisclosure/2021/Feb/71
