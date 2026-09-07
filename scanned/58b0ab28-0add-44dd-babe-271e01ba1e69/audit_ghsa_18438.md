# [M] Jenkins ReadyAPI Functional Testing Plugin vulnerability exposes secrets

## Summary
Severity: Medium
Advisory: GHSA-r496-x769-f8j4
CVE: CVE-2025-53657
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-07-09
Source: https://github.com/advisories/GHSA-r496-x769-f8j4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:soapui-pro-functional-testing` — affected >=0

## Details
Jenkins ReadyAPI Functional Testing Plugin 1.11 and earlier stores SLM License Access Keys, client secrets, and passwords unencrypted in job config.xml files on the Jenkins controller as part of its configuration.

These credentials can be viewed by users with Item/Extended Read permission or access to the Jenkins controller file system.

Additionally, the job configuration form does not mask these credentials, increasing the potential for attackers to observe and capture them.

As of publication of this advisory, there is no fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-53657
- https://github.com/jenkinsci/soapui-pro-functional-testing-plugin
- https://www.jenkins.io/security/advisory/2025-07-09/#SECURITY-3556
- http://www.openwall.com/lists/oss-security/2025/07/09/4
