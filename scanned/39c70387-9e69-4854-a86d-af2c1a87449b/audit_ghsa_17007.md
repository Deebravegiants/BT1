# [H] Ant Media Server vulnerable to a local privilege escalation

## Summary
Severity: High
Advisory: GHSA-qwhw-hh9j-54f5
CVE: CVE-2024-32656
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-22
Source: https://github.com/advisories/GHSA-qwhw-hh9j-54f5
Type: github-advisory

## Affected
- Maven: `io.antmedia:ant-media-server` — affected >=2.6.0 <2.9.0

## Details
### Impact
We have identified a local privilege escalation vulnerability in Ant Media Server which allows any unprivileged operating system user account to escalate privileges to the root user account on the system. This vulnerability arises from Ant Media Server running with Java Management Extensions (JMX) enabled and authentication disabled on localhost on port 5599/TCP. This vulnerability is nearly identical to the local privilege escalation vulnerability CVE-2023-26269 identified in Apache James.
Any unprivileged operating system user can connect to the JMX service running on port 5599/TCP on localhost and leverage the MLet Bean within JMX to load a remote MBean from an attacker-controlled server. This allows an attacker to execute arbitrary code within the Java process run by Ant Media Server and execute code within the context of the “antmedia” service account on the system.

### Patches
2.9.0

### Workarounds
Remote the following parameters from antmedia.service file

```-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.port=5599 -Dcom.sun.management.jmxremote.local.only=true -Dcom.sun.management.jmxremote.host=127.0.0.1 -Djava.rmi.server.hostname=127.0.0.1 -Djava.rmi.server.useLocalHostname=true -Dcom.sun.management.jmxremote.rmi.port=5599```



Thank you [Adam Crosser](https://www.linkedin.com/in/adam-crosser-366263265/) for reporting the issue
[Local Privilege Escalation via Unauthenticated JMX Remote Management Interface (1).pdf](https://github.com/ant-media/Ant-Media-Server/files/15059667/Local.Privilege.Escalation.via.Unauthenticated.JMX.Remote.Management.Interface.1.pdf)

## References
- https://github.com/ant-media/Ant-Media-Server/security/advisories/GHSA-qwhw-hh9j-54f5
- https://nvd.nist.gov/vuln/detail/CVE-2024-32656
- https://github.com/ant-media/Ant-Media-Server/commit/9cb38500729e0ff302da0290b9cfe1ec4dd6c764
- https://github.com/ant-media/Ant-Media-Server
