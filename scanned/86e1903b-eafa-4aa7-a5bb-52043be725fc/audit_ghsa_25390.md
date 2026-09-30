# [H] Jenkins Artifactory Plugin stored old directly entered credentials unencrypted on disk 

## Summary
Severity: High
Advisory: GHSA-cvh8-9j4x-5v4j
CVE: CVE-2018-1000424
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-cvh8-9j4x-5v4j
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:artifactory` — affected >=0 <2.16.2

## Details
An insufficiently protected credentials vulnerability exists in Jenkins Artifactory Plugin 2.16.1 and earlier in ArtifactoryBuilder.java, CredentialsConfig.java that allows attackers with local file system access to obtain old credentials configured for the plugin before it integrated with Credentials Plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000424
- https://jenkins.io/security/advisory/2018-09-25/#SECURITY-265
- http://www.securityfocus.com/bid/106532
