# [M] Regular Expression Denial of Service in hosted-git-info

## Summary
Severity: Medium
Advisory: GHSA-43f8-2h32-f4cj
CVE: CVE-2021-23362
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-43f8-2h32-f4cj
Type: github-advisory

## Affected
- npm: `hosted-git-info` — affected >=0 <2.8.9
- npm: `hosted-git-info` — affected >=3.0.0 <3.0.8

## Details
The npm package `hosted-git-info` before 3.0.8 are vulnerable to Regular Expression Denial of Service (ReDoS) via regular expression shortcutMatch in the fromUrl function in index.js. The affected regular expression exhibits polynomial worst-case time complexity

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23362
- https://github.com/npm/hosted-git-info/pull/76
- https://github.com/npm/hosted-git-info/commit/29adfe5ef789784c861b2cdeb15051ec2ba651a7
- https://github.com/npm/hosted-git-info/commit/8d4b3697d79bcd89cdb36d1db165e3696c783a01
- https://github.com/npm/hosted-git-info/commit/bede0dc38e1785e732bf0a48ba6f81a4a908eba3
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/npm/hosted-git-info
- https://github.com/npm/hosted-git-info/commits/v2
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1088356
- https://snyk.io/vuln/SNYK-JS-HOSTEDGITINFO-1088355
