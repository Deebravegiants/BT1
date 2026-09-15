# [C] Command Injection in Xstream

## Summary
Severity: Critical
Advisory: GHSA-f554-x222-wgf7
CVE: CVE-2013-7285
CWE: CWE-77, CWE-78
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-05-29
Source: https://github.com/advisories/GHSA-f554-x222-wgf7
Type: github-advisory

## Affected
- Maven: `com.thoughtworks.xstream:xstream` — affected >=0 <1.4.7
- Maven: `com.thoughtworks.xstream:xstream` — affected >=1.4.10 <1.4.11

## Details
Xstream API versions up to 1.4.6 and version 1.4.10, if the security framework has not been initialized, may allow a remote attacker to run arbitrary shell commands by manipulating the processed input stream when unmarshaling XML or any supported format. e.g. JSON.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7285
- https://github.com/x-stream/xstream/commit/6344867dce6767af7d0fe34fb393271a6456672d
- https://lists.apache.org/thread.html/6d3d34adcf3dfc48e36342aa1f18ce3c20bb8e4c458a97508d5bfed1@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/dcf8599b80e43a6b60482607adb76c64672772dc2d9209ae2170f369@%3Cissues.activemq.apache.org%3E
- https://www.mail-archive.com/user@xstream.codehaus.org/msg00604.html
- https://www.mail-archive.com/user@xstream.codehaus.org/msg00607.html
- https://www.oracle.com/security-alerts/cpuoct2020.html
- https://x-stream.github.io/CVE-2013-7285.html
- http://blog.diniscruz.com/2013/12/xstream-remote-code-execution-exploit.html
- http://seclists.org/oss-sec/2014/q1/69
- http://web.archive.org/web/20140204133306/http://blog.diniscruz.com/2013/12/xstream-remote-code-execution-exploit.html
