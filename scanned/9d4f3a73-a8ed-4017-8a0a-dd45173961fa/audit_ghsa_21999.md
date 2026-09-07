# [H] ua-parser-js Regular Expression Denial of Service vulnerability

## Summary
Severity: High
Advisory: GHSA-394c-5j6w-4xmx
CVE: CVE-2020-7793
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-394c-5j6w-4xmx
Type: github-advisory

## Affected
- npm: `ua-parser-js` — affected >=0 <0.7.23

## Details
The package ua-parser-js before 0.7.23 are vulnerable to Regular Expression Denial of Service (ReDoS) in multiple regexes (see linked commit for more info).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7793
- https://github.com/faisalman/ua-parser-js/commit/6d1f26df051ba681463ef109d36c9cf0f7e32b18
- https://cert-portal.siemens.com/productcert/pdf/ssa-637483.pdf
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBFAISALMAN-1050388
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1050387
- https://snyk.io/vuln/SNYK-JS-UAPARSERJS-1023599
