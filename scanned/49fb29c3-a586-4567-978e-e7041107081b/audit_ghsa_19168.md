# [H] JSONPath Plus allows Remote Code Execution

## Summary
Severity: High
Advisory: GHSA-hw8r-x6gr-5gjp
CVE: CVE-2025-1302
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-02-15
Source: https://github.com/advisories/GHSA-hw8r-x6gr-5gjp
Type: github-advisory

## Affected
- npm: `jsonpath-plus` — affected >=0 <10.3.0

## Details
Versions of the package jsonpath-plus before 10.3.0 are vulnerable to Remote Code Execution (RCE) due to improper input sanitization. An attacker can execute aribitrary code on the system by exploiting the unsafe default usage of eval='safe' mode.

**Note:**

This is caused by an incomplete fix for CVE-2024-21534.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21534
- https://nvd.nist.gov/vuln/detail/CVE-2025-1302
- https://github.com/JSONPath-Plus/JSONPath/commit/30942896d27cb8a806b965a5ca9ef9f686be24ee
- https://gist.github.com/nickcopi/11ba3cb4fdee6f89e02e6afae8db6456
- https://github.com/JSONPath-Plus/JSONPath
- https://github.com/JSONPath-Plus/JSONPath/blob/8e4acf8aff5f446aa66323e12394ac5615c3b260/src/Safe-Script.js#L127
- https://security.snyk.io/vuln/SNYK-JS-JSONPATHPLUS-8719585
