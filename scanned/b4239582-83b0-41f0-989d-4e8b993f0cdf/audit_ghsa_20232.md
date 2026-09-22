# [M] Agent-to-controller security bypass in Jenkins xUnit Plugin

## Summary
Severity: Medium
Advisory: GHSA-298j-9q4w-6rm4
CVE: CVE-2022-34181
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-24
Source: https://github.com/advisories/GHSA-298j-9q4w-6rm4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:xunit` — affected >=0 <3.1.0

## Details
xUnit Plugin 3.0.8 and earlier implements an agent-to-controller message that creates a user-specified directory if it doesn’t exist, and parsing files inside it as test results.

This allows attackers able to control agent processes to create an arbitrary directory on the Jenkins controller or to obtain test results from existing files in an attacker-specified directory.

xUnit Plugin 3.1.0 changes the message type from agent-to-controller to controller-to-agent, preventing execution on the controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-34181
- https://github.com/jenkinsci/xunit-plugin/commit/6976b5da114845a7936ea36d5783a65cd91f9897
- https://github.com/jenkinsci/xunit-plugin
- https://www.jenkins.io/security/advisory/2022-06-22/#SECURITY-2549
