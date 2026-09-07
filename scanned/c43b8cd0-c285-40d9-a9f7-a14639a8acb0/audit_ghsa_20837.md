# [M] Jenkins SmallTest Plugin missing hostname validation

## Summary
Severity: Medium
Advisory: GHSA-7jwg-hq85-c6m6
CVE: CVE-2022-41243
CWE: CWE-297
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-22
Source: https://github.com/advisories/GHSA-7jwg-hq85-c6m6
Type: github-advisory

## Affected
- Maven: `com.smalltest:smalltest` — affected >=0

## Details
Jenkins SmallTest Plugin 1.0.4 and earlier does not perform hostname validation when connecting to the configured View26 server that could be abused using a man-in-the-middle attack to intercept these connections. There is currently no known workaround or fix for this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41243
- https://github.com/jenkinsci/smalltest-plugin
- https://www.jenkins.io/security/advisory/2022-09-21/#SECURITY-2068
