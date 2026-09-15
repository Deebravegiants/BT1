# [H] node-static and @nubosoftware/node-static vulnerable to Directory Traversal

## Summary
Severity: High
Advisory: GHSA-5g97-whc9-8g7j
CVE: CVE-2023-26111
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-06
Source: https://github.com/advisories/GHSA-5g97-whc9-8g7j
Type: github-advisory

## Affected
- npm: `node-static` — affected >=0
- npm: `@nubosoftware/node-static` — affected >=0

## Details
node-static and its fork, @nubosoftware/node-static, are vulnerable to Directory Traversal due to improper file path sanitization in the startsWith() method in the servePath function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-26111
- https://gist.github.com/lirantal/c80b28e7bee148dc287339cb483e42bc
- https://github.com/cloudhead/node-static
- https://github.com/cloudhead/node-static/blob/master/lib/node-static.js#23L160-L163
- https://security.snyk.io/vuln/SNYK-JS-NODESTATIC-3149928
- https://security.snyk.io/vuln/SNYK-JS-NUBOSOFTWARENODESTATIC-3149927
