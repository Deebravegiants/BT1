# [H] Arbitrary code execution due to incomplete sandbox protection in Jenkins Pipeline

## Summary
Severity: High
Advisory: GHSA-mhwq-4mh7-fv7c
CVE: CVE-2017-1000096
CWE: CWE-732
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mhwq-4mh7-fv7c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps` — affected >=0 <2.36.1

## Details
Arbitrary code execution due to incomplete sandbox protection: Constructors, instance variable initializers, and instance initializers in Pipeline scripts were not subject to sandbox protection, and could therefore execute arbitrary code. This could be exploited e.g. by regular Jenkins users with the permission to configure Pipelines in Jenkins, or by trusted committers to repositories containing Jenkinsfiles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000096
- https://jenkins.io/security/advisory/2017-07-10
- http://www.securityfocus.com/bid/99571
