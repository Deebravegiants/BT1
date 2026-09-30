# [H] is_js vulnerable to Regular Expression Denial of Service

## Summary
Severity: High
Advisory: GHSA-pvrw-g6fx-mcx2
CVE: CVE-2020-26302
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-07-06
Source: https://github.com/advisories/GHSA-pvrw-g6fx-mcx2
Type: github-advisory

## Affected
- npm: `is_js` — affected >=0

## Details
is.js is a general-purpose check library. Versions 0.9.0 and prior contain one or more regular expressions that are vulnerable to Regular Expression Denial of Service (ReDoS). is.js uses a regex copy-pasted from a gist to validate URLs. Trying to validate a malicious string can cause the regex to loop "forever." This vulnerability was found using a CodeQL query which identifies inefficient regular expressions. is.js has no patch for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26302
- https://github.com/arasatasaygin/is.js/issues/320
- https://github.com/arasatasaygin/is.js
- https://securitylab.github.com/advisories/GHSL-2020-295-redos-is.js
