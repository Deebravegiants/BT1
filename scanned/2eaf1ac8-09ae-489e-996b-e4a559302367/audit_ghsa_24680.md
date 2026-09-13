# [M] Parameterized Trigger Plugin fails to check Item/Build permission

## Summary
Severity: Medium
Advisory: GHSA-mc22-25r3-2w9w
CVE: CVE-2017-1000084
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mc22-25r3-2w9w
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:parameterized-trigger` — affected >=0 <2.35.1

## Details
Parameterized Trigger Plugin fails to check Item/Build permission: The Parameterized Trigger Plugin did not check the build authentication it was running as and allowed triggering any other project in Jenkins. The plugin has been adapted to now check for Item/Build permission before triggering a downstream build.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000084
- https://github.com/jenkinsci/parameterized-trigger-plugin/pull/114
- https://github.com/fbelzunc/parameterized-trigger-plugin/commit/345d54f8f031bef68ecb6fd4e7eee0be720162e4
- https://github.com/jenkinsci/parameterized-trigger-plugin
- https://issues.jenkins.io/browse/JENKINS-45471
- https://jenkins.io/security/advisory/2017-07-10
