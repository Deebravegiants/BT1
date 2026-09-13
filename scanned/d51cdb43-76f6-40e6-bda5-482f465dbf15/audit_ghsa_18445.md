# [M] Jenkins Sensedia API Platform Plugin vulnerability exposes unencrypted tokens in its global configuration file

## Summary
Severity: Medium
Advisory: GHSA-93j6-jcjw-3rwp
CVE: CVE-2025-53673
CWE: CWE-311
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-93j6-jcjw-3rwp
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:sensedia-api-platform` — affected >=0

## Details
Jenkins Sensedia Api Platform tools Plugin 1.0 stores the Sensedia API Manager integration token unencrypted in its global configuration file `com.sensedia.configuration.SensediaApiConfiguration.xml` on the Jenkins controller as part of its configuration.

This token can be viewed by users with access to the Jenkins controller file system.

Additionally, the global configuration form does not mask the token, increasing the potential for attackers to observe and capture it.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53673
- https://github.com/jenkinsci/sensedia-api-platform-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3551
- http://www.openwall.com/lists/oss-security/2025/07/09/4
