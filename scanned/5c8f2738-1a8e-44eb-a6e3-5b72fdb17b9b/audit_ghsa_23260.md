# [M] Jenkins Maven Artifact ChoiceListProvider (Nexus) Plugin CSRF vulnerability and missing permission checks

## Summary
Severity: Medium
Advisory: GHSA-fjh2-qhfh-rvfc
CVE: CVE-2018-1999030
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-fjh2-qhfh-rvfc
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:maven-artifact-choicelistprovider` — affected >=0 <1.3.2

## Details
An exposure of sensitive information vulnerability exists in Jenkins Maven Artifact ChoiceListProvider (Nexus) Plugin 1.3.1 and earlier in ArtifactoryChoiceListProvider.java, NexusChoiceListProvider.java, Nexus3ChoiceListProvider.java that allows attackers to capture credentials with a known credentials ID stored in Jenkins.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1999030
- https://github.com/jenkinsci/maven-artifact-choicelistprovider-plugin/commit/2d2e20cc00a29abf435afcad12cfc9ddadf76d89
- https://github.com/jenkinsci/maven-artifact-choicelistprovider-plugin/commit/5a3a3ff1e7416623c531601620305640ef4c8e28
- https://github.com/jenkinsci/maven-artifact-choicelistprovider-plugin/commit/99d97c028fbc0672b729d052d4bfc4dfa9674f23
- https://github.com/jenkinsci/maven-artifact-choicelistprovider-plugin
- https://jenkins.io/security/advisory/2018-07-30/#SECURITY-1022
