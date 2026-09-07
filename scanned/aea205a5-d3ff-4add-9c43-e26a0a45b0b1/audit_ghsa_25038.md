# [M] Jenkins SCTMExecutor Plugin stores credentials in plain text 

## Summary
Severity: Medium
Advisory: GHSA-rxph-cq38-gm3g
CVE: CVE-2019-16568
CWE: CWE-319
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rxph-cq38-gm3g
Type: github-advisory

## Affected
- Maven: `hudson.plugins.sctmexecutor:SCTMExecutor` — affected >=0

## Details
Jenkins SCTMExecutor Plugin 2.2 and earlier transmits previously configured service credentials in plain text as part of the global configuration, as well as individual jobs' configurations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16568
- https://github.com/jenkins-infra/update-center2/pull/324
- https://jenkins.io/security/advisory/2019-12-17/#SECURITY-1521
- http://www.openwall.com/lists/oss-security/2019/12/17/1
