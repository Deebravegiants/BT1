# [H] Apache ActiveMQ Deserialization of Untrusted Data vulnerability

## Summary
Severity: High
Advisory: GHSA-53v4-42fg-g287
CVE: CVE-2022-41678
CWE: CWE-287, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-53v4-42fg-g287
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:apache-activemq` — affected >=0 <5.16.6
- Maven: `org.apache.activemq:apache-activemq` — affected >=5.17.0 <5.17.4

## Details
Once an user is authenticated on Jolokia, he can potentially trigger arbitrary code execution. 

In details, in ActiveMQ configurations, jetty allows org.jolokia.http.AgentServlet to handler request to /api/jolokia

org.jolokia.http.HttpRequestHandler#handlePostRequest is able to create JmxRequest through JSONObject. And calls to org.jolokia.http.HttpRequestHandler#executeRequest.

Into deeper calling stacks, org.jolokia.handler.ExecHandler#doHandleRequest is able to invoke through refection.

And then, RCE is able to be achieved via jdk.management.jfr.FlightRecorderMXBeanImpl which exists on Java version above 11.

1 Call newRecording.

2 Call setConfiguration. And a webshell data hides in it.

3 Call startRecording.

4 Call copyTo method. The webshell will be written to a .jsp file.

The mitigation is to restrict (by default) the actions authorized on Jolokia, or disable Jolokia.
A more restrictive Jolokia configuration has been defined in default ActiveMQ distribution. We encourage users to upgrade to ActiveMQ distributions version including updated Jolokia configuration: 5.16.6, 5.17.4, 5.18.0, 6.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41678
- https://github.com/apache/activemq/pull/958
- https://github.com/apache/activemq/commit/5c8d457d9
- https://github.com/apache/activemq/commit/6120169e563b55323352431dfe9ac67a8b4de6c2
- https://github.com/apache/activemq/commit/bf65929fd
- https://github.com/apache/activemq/commit/d8ce1d9ff
- https://activemq.apache.org/security-advisories.data/CVE-2022-41678-announcement.txt
- https://github.com/apache/activemq
- https://lists.apache.org/thread/7g17kwbtjl011mm4tr8bn1vnoq9wh4sl
- https://lists.debian.org/debian-lts-announce/2024/10/msg00027.html
- https://security.netapp.com/advisory/ntap-20240216-0004
- https://www.openwall.com/lists/oss-security/2023/11/28/1
- http://www.openwall.com/lists/oss-security/2023/11/28/1
