# [M] Jenkins NUnit Plugin vulnerable to Protection Mechanism Failure

## Summary
Severity: Medium
Advisory: GHSA-8cxw-wvhc-p4x4
CVE: CVE-2022-43414
CWE: CWE-552, CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-8cxw-wvhc-p4x4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:nunit` — affected >=0 <0.28

## Details
Jenkins NUnit Plugin 0.27 and earlier implements an agent-to-controller message that parses files inside a user-specified directory as test results, allowing attackers able to control agent processes to obtain test results from files in an attacker-specified directory on the Jenkins controller. NUnit Plugin 0.28 changes the message type from agent-to-controller to controller-to-agent, preventing execution on the controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43414
- https://github.com/jenkinsci/nunit-plugin/commit/e97a5aa804019ab345f50014f56ece23882c7475
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2551
- http://www.openwall.com/lists/oss-security/2022/10/19/3
