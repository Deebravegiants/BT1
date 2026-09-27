# [H] Jenkins Katalon Plugin vulnerable to Protection Mechanism Failure

## Summary
Severity: High
Advisory: GHSA-q6f6-6c4p-xph4
CVE: CVE-2022-43416
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-19
Source: https://github.com/advisories/GHSA-q6f6-6c4p-xph4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:katalon` — affected >=0 <1.0.33

## Details
Jenkins Katalon Plugin 1.0.32 and earlier implements an agent/controller message that does not limit where it can be executed and allows invoking Katalon with configurable arguments.

It allows attackers able to control agent processes to invoke Katalon on the Jenkins controller with attacker-controlled version, install location, and arguments. Attackers additionally able to create files on the Jenkins controller (e.g., attackers with Item/Configure permission could archive artifacts) can invoke arbitrary OS commands.

Katalon Plugin 1.0.33 changes the message type to controller-to-agent, preventing execution on the controller.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-43416
- https://github.com/jenkinsci/katalon-plugin/commit/0ee4b34afdcba367b547aa0a706cb1c66ac9f45a
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2844
- http://www.openwall.com/lists/oss-security/2022/10/19/3
