# [M] Password parameter default values exposed by Jenkins Pipeline: Build Step Plugin

## Summary
Severity: Medium
Advisory: GHSA-g84f-cmc8-682c
CVE: CVE-2022-25184
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-g84f-cmc8-682c
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:pipeline-build-step` — affected >=0 <2.15.1

## Details
Jenkins Pipeline: Build Step Plugin 2.15 and earlier reveals password parameter default values when generating a pipeline script using the Pipeline Snippet Generator, allowing attackers with Item/Read permission to retrieve the default password parameter value from jobs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-25184
- https://github.com/jenkinsci/pipeline-build-step-plugin/commit/c06f65425fe9696d2237f591959dd4b5c6083fd9
- https://github.com/jenkinsci/pipeline-build-step-plugin
- https://www.jenkins.io/security/advisory/2022-02-15/#SECURITY-2519
