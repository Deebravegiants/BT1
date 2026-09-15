# [C] node-import `params` argument can be controlled by users without any sanitization

## Summary
Severity: Critical
Advisory: GHSA-pc62-cq5x-3j5g
CVE: CVE-2020-7678
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-26
Source: https://github.com/advisories/GHSA-pc62-cq5x-3j5g
Type: github-advisory

## Affected
- npm: `node-import` — affected >=0

## Details
This affects all versions of package node-import. The `params` argument of module function can be controlled by users without any sanitization. This is then provided to the “eval” function located in line 79 in the index file `index.js`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7678
- https://github.com/mahdaen/node-import
- https://github.com/mahdaen/node-import/blob/master/index.js%23L79
- https://security.snyk.io/vuln/SNYK-JS-NODEIMPORT-571691
