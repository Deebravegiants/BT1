# [C] XML external entity vulnerability in Jenkins Nuget Plugin

## Summary
Severity: Critical
Advisory: GHSA-p674-hh8x-rv5h
CVE: CVE-2021-21658
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-p674-hh8x-rv5h
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nuget` — affected >=0 <1.1

## Details
Jenkins Nuget Plugin 1.0 and earlier does not configure its XML parser to prevent XML external entity (XXE) attacks. This XML parser is used for the \"Build on NuGet updates\" feature.

This allows attackers with the ability to control the contents of the `packages.config` file in a workspace to have Jenkins parse a crafted XML document that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Jenkins Nuget Plugin 1.1 disables external entity resolution for its XML parser.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21658
- https://github.com/jenkinsci/nuget-plugin/commit/542bf38ac52f045741a5670e1644af351878f7e0
- https://github.com/jenkinsci/nuget-plugin/commit/c8ed4cb5b1c42f3c407f9f418b4e0b4274bea5a9
- https://github.com/jenkinsci/nuget-plugin
- https://www.jenkins.io/security/advisory/2021-05-25/#SECURITY-2340
- http://www.openwall.com/lists/oss-security/2021/05/25/3
