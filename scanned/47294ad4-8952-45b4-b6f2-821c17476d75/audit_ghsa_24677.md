# [M] Missing permission checks in Jenkins Warnings Next Generation Plugin allow listing workspace contents

## Summary
Severity: Medium
Advisory: GHSA-7j3x-xm4j-jfj7
CVE: CVE-2021-21626
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7j3x-xm4j-jfj7
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugins:warnings-ng` — affected >=0 <8.5.0

## Details
Jenkins Warnings Next Generation Plugin 8.4.4 and earlier does not perform permission checks in methods implementing form validation.

This allows attackers with Item/Read permission but without Item/Workspace or Item/Configure permission to check whether attacker-specified file patterns match workspace contents. A sequence of requests can be used to effectively list workspace contents.

Jenkins Warnings Next Generation Plugin 8.5.0 requires Item/Configure permission to validate patterns with workspace contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21626
- https://github.com/jenkinsci/warnings-ng-plugin
- https://www.jenkins.io/security/advisory/2021-03-18/#SECURITY-2041
- http://www.openwall.com/lists/oss-security/2021/03/18/5
