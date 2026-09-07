# [H] Arbitrary code execution due to incomplete sandbox protection in Pipeline: Supporting APIs Plugin

## Summary
Severity: High
Advisory: GHSA-p3g4-9xfv-wq9v
CVE: CVE-2018-1000058
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-p3g4-9xfv-wq9v
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-support` — affected >=0 <2.18

## Details
Jenkins Pipeline: Supporting APIs Plugin 2.17 and earlier have an arbitrary code execution due to incomplete sandbox protection: Methods related to Java deserialization like readResolve implemented in Pipeline scripts were not subject to sandbox protection, and could therefore execute arbitrary code. This could be exploited e.g. by regular Jenkins users with the permission to configure Pipelines in Jenkins, or by trusted committers to repositories containing Jenkinsfiles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000058
- https://jenkins.io/security/advisory/2018-02-05
- http://www.securityfocus.com/bid/103034
