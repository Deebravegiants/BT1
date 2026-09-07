# [H] Jenkins Nexus Platform Plugin missing permission check

## Summary
Severity: High
Advisory: GHSA-9vrm-747r-668v
CVE: CVE-2023-50767
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-12-13
Source: https://github.com/advisories/GHSA-9vrm-747r-668v
Type: github-advisory

## Affected
- Maven: `org.sonatype.nexus.ci:nexus-jenkins-plugin` — affected >=0 <3.18.1-01

## Details
Jenkins Nexus Platform Plugin 3.18.0-03 and earlier does not perform permission checks in methods implementing form validation.

This allows attackers with Overall/Read permission to send an HTTP request to an attacker-specified URL and parse the response as XML.

Additionally, the plugin does not configure its XML parser to prevent XML external entity (XXE) attacks, so attackers can have Jenkins parse a crafted XML response that uses external entities for extraction of secrets from the Jenkins controller or server-side request forgery.

Additionally, these form validation methods do not require POST requests, resulting in a cross-site request forgery (CSRF) vulnerability.

Nexus Platform Plugin 3.18.1-01 configures its XML parser to prevent XML external entity (XXE) attacks.

Additionally, POST requests and Overall/Administer permission are required for the affected HTTP endpoints.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50767
- https://github.com/jenkinsci/nexus-platform-plugin/pull/291
- https://github.com/jenkinsci/nexus-platform-plugin/commit/1d5e1e9e457af5e8ce8c9a403933d6cb73542dbd
- https://github.com/jenkinsci/nexus-platform-plugin
- https://www.jenkins.io/security/advisory/2023-12-13/#SECURITY-3204
- http://www.openwall.com/lists/oss-security/2023/12/13/4
