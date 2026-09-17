# [H] Buffer Overflow in Apache Mina SSHD

## Summary
Severity: High
Advisory: GHSA-9279-7hph-r3xw
CVE: CVE-2021-30129
CWE: CWE-772
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-02
Source: https://github.com/advisories/GHSA-9279-7hph-r3xw
Type: github-advisory

## Affected
- Maven: `org.apache.sshd:sshd-mina` — affected >=2.0.0 <2.7.0
- Maven: `org.apache.sshd:sshd-core` — affected >=2.0.0 <2.7.0

## Details
A vulnerability in sshd-core of Apache Mina SSHD allows an attacker to overflow the server causing an OutOfMemory error. This issue affects the SFTP and port forwarding features of Apache Mina SSHD version 2.0.0 and later versions. It was addressed in Apache Mina SSHD 2.7.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-30129
- https://issues.apache.org/jira/browse/SSHD-1125
- https://lists.apache.org/thread.html/r6d4f78e192a0c8eabd671a018da464024642980ecd24096bde6db36f%40%3Cusers.mina.apache.org%3E
- https://lists.apache.org/thread.html/r6d4f78e192a0c8eabd671a018da464024642980ecd24096bde6db36f@%3Cusers.mina.apache.org%3E
- https://lists.apache.org/thread.html/red01829efa2a8c893c4baff4f23c9312bd938543a9b8658e172b853b@%3Cannounce.apache.org%3E
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
- http://www.openwall.com/lists/oss-security/2021/07/12/1
