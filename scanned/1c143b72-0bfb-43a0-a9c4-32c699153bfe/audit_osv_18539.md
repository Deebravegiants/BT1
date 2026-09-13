# [M] CVE-2020-28500

## Summary
Severity: Medium
Advisory: CVE-2020-28500
Aliases: GHSA-29mw-wpgm-hmr9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-02-15
Source: https://osv.dev/vulnerability/CVE-2020-28500
Type: osv

## Details
Lodash versions prior to 4.17.21 are vulnerable to Regular Expression Denial of Service (ReDoS) via the toNumber, trim and trimEnd functions.

## References
- https://github.com/lodash/lodash/blob/npm/trimEnd.js%23L8
- https://security.netapp.com/advisory/ntap-20210312-0006/
- https://www.oracle.com//security-alerts/cpujul2021.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-637483.pdf
- https://github.com/lodash/lodash/pull/5065
- https://www.oracle.com/security-alerts/cpujan2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
- https://snyk.io/vuln/SNYK-JAVA-ORGFUJIONWEBJARS-1074896
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARS-1074894
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1074892
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBLODASH-1074895
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1074893
- https://snyk.io/vuln/SNYK-JS-LODASH-1018905
