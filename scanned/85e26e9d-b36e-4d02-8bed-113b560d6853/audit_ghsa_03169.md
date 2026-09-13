# [M] Regular expression denial of service in codemirror

## Summary
Severity: Medium
Advisory: GHSA-4gw3-8f77-f72c
CVE: CVE-2020-7760
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-4gw3-8f77-f72c
Type: github-advisory

## Affected
- npm: `codemirror` — affected >=0 <5.58.2

## Details
This affects the package codemirror before 5.58.2; the package org.apache.marmotta.webjars:codemirror before 5.58.2.
 The vulnerable regular expression is located in https://github.com/codemirror/CodeMirror/blob/cdb228ac736369c685865b122b736cd0d397836c/mode/javascript/javascript.jsL129. The ReDOS vulnerability of the regex is mainly due to the sub-pattern (s|/*.*?*/)*

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7760
- https://github.com/codemirror/CodeMirror/commit/55d0333907117c9231ffdf555ae8824705993bbb
- https://snyk.io/vuln/SNYK-JAVA-ORGAPACHEMARMOTTAWEBJARS-1024450
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1024449
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1024445
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBCODEMIRROR-1024448
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBCOMPONENTS-1024446
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1024447
- https://snyk.io/vuln/SNYK-JS-CODEMIRROR-1016937
- https://www.debian.org/security/2020/dsa-4789
- https://www.npmjs.com/package/codemirror
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://www.oracle.com/security-alerts/cpuApr2021.html
- https://www.oracle.com/security-alerts/cpuapr2022.html
