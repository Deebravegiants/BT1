# [M] Buffer overflow in Jenkins WMI Windows Agents plugin

## Summary
Severity: Medium
Advisory: GHSA-xhw3-wmx2-76wf
CVE: CVE-2022-30950
CWE: CWE-120
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-18
Source: https://github.com/advisories/GHSA-xhw3-wmx2-76wf
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:windows-slaves` — affected >=0 <1.8.1

## Details
WMI Windows Agents Plugin 1.8 and earlier includes the Windows Remote Command library. It provides a general-purpose remote command execution capability that Jenkins uses to check if Java is available, and if not, to install it.

This library has a buffer overflow vulnerability that may allow users able to connect to a named pipe to execute commands on the Windows agent machine.

Additionally, while the processes are started as the user who connects to the named pipe, no access control takes place, potentially allowing users to start processes even if they’re not allowed to log in.

WMI Windows Agents Plugin 1.8.1 no longer includes the Windows Remote Command library. A Java runtime is expected to be available on agent machines and WMI Windows Agents Plugin 1.8.1 does not install a JDK automatically otherwise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-30950
- https://github.com/jenkinsci/windows-slaves-plugin/commit/4638cf0e56caf839eadfdf0fab545abd2a9ac65e
- https://github.com/jenkinsci/windows-slaves-plugin
- https://www.jenkins.io/security/advisory/2022-05-17/#SECURITY-2604
- http://www.openwall.com/lists/oss-security/2022/05/17/8
