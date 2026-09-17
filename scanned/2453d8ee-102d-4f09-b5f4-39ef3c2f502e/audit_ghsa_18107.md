# [M] Jenkins has a log message injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qrh5-jg98-cr48
CVE: CVE-2025-59476
CWE: CWE-117, CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-qrh5-jg98-cr48
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.516.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.517 <2.528

## Details
In Jenkins 2.527 and earlier, LTS 2.516.2 and earlier, the log formatter that prepares log messages for console output (including `jenkins.log` and equivalent) does not restrict or transform the characters that can be inserted from user-specified content in log messages.

This allows attackers able to control log message contents to insert line break characters, followed by forged log messages that may mislead administrators reviewing log output.

Jenkins 2.528, LTS 2.516.3 adds an indicator at the beginning of a line that was inserted as part of log message content: `[CR]`, `[LF]`, or `[CRLF]` (representing the kind of line break), followed by `>` .

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59476
- https://github.com/jenkinsci/jenkins
- https://www.jenkins.io/security/advisory/2025-09-17/#SECURITY-3424
- http://www.openwall.com/lists/oss-security/2025/09/17/1
