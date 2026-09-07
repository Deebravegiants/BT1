# [M] Cross-site Scripting in vis-timeline

## Summary
Severity: Medium
Advisory: GHSA-9mrv-456v-pf22
CVE: CVE-2020-28487
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2021-04-13
Source: https://github.com/advisories/GHSA-9mrv-456v-pf22
Type: github-advisory

## Affected
- npm: `vis-timeline` — affected >=0 <7.4.4

## Details
This affects the package vis-timeline before 7.4.4.
 An attacker with the ability to control the items of a Timeline element can inject additional script code into the generated application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28487
- https://github.com/visjs/vis-timeline/issues/838
- https://github.com/visjs/vis-timeline/pull/840
- https://github.com/visjs/vis-timeline/commit/a7ca349c7b3b6080efd05776ac77bb27176d4d3f
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWERGITHUBVISJS-1063502
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1063501
- https://snyk.io/vuln/SNYK-JS-VISTIMELINE-1063500
