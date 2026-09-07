# [H] Linkify Allows Prototype Pollution & HTML Attribute Injection (XSS)

## Summary
Severity: High
Advisory: GHSA-95jq-xph2-cx9h
CVE: CVE-2025-8101
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-07-26
Source: https://github.com/advisories/GHSA-95jq-xph2-cx9h
Type: github-advisory

## Affected
- npm: `linkifyjs` — affected >=4.3.1 <4.3.2

## Details
Prototype Pollution in internal `assign()` helper in Linkify allows remote attackers to execute arbitrary JavaScript (Stored or Reflected XSS) via injection of event handlers through unfiltered proto property. This issue affects Linkify version 4.3.1 and is fixed in 4.3.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8101
- https://github.com/nfrasser/linkifyjs/commit/931d3e28b68951b8f898ea4d6504696346b485b0
- https://caverav.cl/posts/linkify-xss/linkify-xss
- https://fluidattacks.com/advisories/charly
- https://github.com/nfrasser/linkifyjs
- https://github.com/nfrasser/linkifyjs/releases/tag/v4.3.2
- https://www.npmjs.com/package/linkifyjs
