# [M] Missing permission checks in Jenkins Config File Provider Plugin allow enumerating configuration file IDs

## Summary
Severity: Medium
Advisory: GHSA-2959-fj73-hm8p
CVE: CVE-2021-21645
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2959-fj73-hm8p
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:config-file-provider` — affected >=0 <3.7.1

## Details
Jenkins Config File Provider Plugin 3.7.0 and earlier does not perform permission checks in several HTTP endpoints.

This allows attackers with Overall/Read permission to enumerate configuration file IDs.

An enumeration of configuration file IDs in Jenkins Config File Provider Plugin 3.7.1 requires the appropriate permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21645
- https://github.com/jenkinsci/config-file-provider-plugin/commit/b7f3c5150ad557e86414122c69be20075aee27fa
- https://github.com/jenkinsci/config-file-provider-plugin
- https://www.jenkins.io/security/advisory/2021-04-21/#SECURITY-2203
- http://www.openwall.com/lists/oss-security/2021/04/21/2
