# [H] Jenkins Pipeline: Stage View Plugin allows CSRF protection bypass of any target URL in Jenkins

## Summary
Severity: High
Advisory: GHSA-g975-f26h-93g8
CVE: CVE-2022-43408
CWE: CWE-352, CWE-838
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-g975-f26h-93g8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.pipeline-stage-view:pipeline-stage-view` — affected >=2.25 <2.27
- Maven: `org.jenkins-ci.plugins.pipeline-stage-view:pipeline-stage-view` — affected >=0 <2.24.2

## Details
Jenkins Pipeline: Stage View Plugin provides a visualization of Pipeline builds. It also allows users to interact with `input` steps from Pipeline: Input Step Plugin.

Pipeline: Stage View Plugin 2.26 and earlier does not correctly encode the ID of `input` steps when using it to generate URLs to proceed or abort Pipeline builds.

This allows attackers able to configure Pipelines to specify `input` step IDs resulting in URLs that would bypass the CSRF protection of any target URL in Jenkins.

Pipeline: Stage View Plugin 2.27 correctly encodes the ID of `input` steps when using it to generate URLs to proceed or abort Pipeline builds.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43408
- https://github.com/jenkinsci/pipeline-stage-view-plugin/commit/cee275109ee748fa9f599ec60159807a28a2933f
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2828
- http://www.openwall.com/lists/oss-security/2022/10/19/3
