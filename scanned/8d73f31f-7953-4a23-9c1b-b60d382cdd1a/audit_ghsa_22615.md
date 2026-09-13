# [H] Apache Geronimo JMX Remoting functionality allows remote code execution in 3.x before v3.0.1

## Summary
Severity: High
Advisory: GHSA-v64w-96p6-fx7w
CVE: CVE-2013-1777
CWE: CWE-94
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v64w-96p6-fx7w
Type: github-advisory

## Affected
- Maven: `org.apache.geronimo.framework:geronimo-jmx-remoting` — affected >=3.0-beta-1 <3.0.1

## Details
The JMX Remoting functionality in Apache Geronimo 3.x before 3.0.1, as used in IBM WebSphere Application Server (WAS) Community Edition 3.0.0.3 and other products, does not properly implement the RMI classloader, which allows remote attackers to execute arbitrary code by using the JMX connector to send a crafted serialized object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-1777
- https://github.com/apache/geronimo/commit/ee031c5e62b0d358250d06c2aa6722518579a6c5
- https://github.com/apache/geronimo
- https://issues.apache.org/jira/browse/GERONIMO-6477
- http://archives.neohapsis.com/archives/bugtraq/2013-07/0008.html
- http://geronimo.apache.org/30x-security-report.html
- http://svn.apache.org/viewvc/geronimo/server/trunk
- http://svn.apache.org/viewvc?view=revision&revision=1458113
- http://www-01.ibm.com/support/docview.wss?uid=swg21643282
