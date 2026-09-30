# [M] Excessive memory allocation in graph URLs leads to denial of service in Jenkins

## Summary
Severity: Medium
Advisory: GHSA-cxqw-vjcr-gp5g
CVE: CVE-2021-21607
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-cxqw-vjcr-gp5g
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.263.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.264 <2.275

## Details
Jenkins renders several different graphs for features like agent and label usage statistics, memory usage, or various plugin-provided statistics.

Jenkins 2.274 and earlier, LTS 2.263.1 and earlier does not limit the graph size provided as query parameters.

This allows attackers to request or to have legitimate Jenkins users request crafted URLs that rapidly use all available memory in Jenkins, potentially leading to out of memory errors.

Jenkins 2.275, LTS 2.263.2 limits the maximum size of graphs to an area of 10 million pixels. If a larger size is requested, the default size for the graph will be rendered instead.

This threshold can be configured by setting the [Java system property](https://www.jenkins.io/doc/book/managing/system-properties/) `hudson.util.Graph.maxArea` to a different number on startup.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21607
- https://github.com/jenkinsci/jenkins/commit/a890d68699ad6ca0c8fbc297a1d4b7ebf23f384b
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2021-01-13/#SECURITY-2025
