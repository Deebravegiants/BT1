# [M] Uncontrolled Resource Consumption in transpile

## Summary
Severity: Medium
Advisory: GHSA-7xrj-f5rp-j55h
CVE: CVE-2021-23429
CWE: CWE-400, CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-02
Source: https://github.com/advisories/GHSA-7xrj-f5rp-j55h
Type: github-advisory

## Affected
- npm: `transpile` — affected >=0

## Details
All versions of package transpile are vulnerable to Denial of Service (DoS) due to a lack of input sanitization or whitelisting, coupled with improper exception handling in the .to() function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23429
- https://github.com/stealjs/transpile
- https://github.com/stealjs/transpile/blob/56aaeb26f69496e45a60c03dc92653d53021d4ac/main.js%23L53
- https://snyk.io/vuln/SNYK-JS-TRANSPILE-1290774
