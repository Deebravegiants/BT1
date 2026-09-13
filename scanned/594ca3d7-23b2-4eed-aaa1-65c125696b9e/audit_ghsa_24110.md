# [H] Maven Extension plugin for Gradle Enterprise vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-vp55-fhxx-vcx8
CVE: CVE-2020-15777
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-vp55-fhxx-vcx8
Type: github-advisory

## Affected
- Maven: `com.gradle:gradle-enterprise-maven-extension` — affected >=0 <1.6

## Details
An issue was discovered in the Maven Extension plugin before 1.6 for Gradle Enterprise. It is vulnerable to, in the worst case, Remote Code Execution, and in the general case, local privilege escalation. Internally, the plugin uses a socket connection to send serialized Java objects that are deserialized by a Java standard library ObjectInputStream. This ObjectInputStream was not restricted to a list of trusted classes, thus allowing an attacker to send a malicious deserialization gadget chain to achieve code execution. The socket was not bound exclusively to localhost. The port this socket is assigned to is randomly selected by the JVM and is not intentionally exposed to the public (either by design or documentation).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-15777
- https://docs.gradle.com/enterprise/maven-extension/#1_6
- https://docs.gradle.com/enterprise/maven-extension/#release_history
- https://security.gradle.com/advisory/CVE-2020-15777
