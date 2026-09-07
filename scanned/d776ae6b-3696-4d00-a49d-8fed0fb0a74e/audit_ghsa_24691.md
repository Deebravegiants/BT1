# [M] Jenkins Build Step Plugin fails to check Item/Build permission

## Summary
Severity: Medium
Advisory: GHSA-8jx9-7j5m-79x4
CVE: CVE-2017-1000089
CWE: CWE-276
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8jx9-7j5m-79x4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-build-step` — affected >=0 <2.5.1

## Details
Builds in Jenkins are associated with an authentication that controls the permissions that the build has to interact with other elements in Jenkins. The Pipeline: Build Step Plugin did not check the build authentication it was running as and allowed triggering any other project in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000089
- https://jenkins.io/security/advisory/2017-07-10
