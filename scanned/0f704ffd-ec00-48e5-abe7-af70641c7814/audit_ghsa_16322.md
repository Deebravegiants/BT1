# [H] Undertow Uncontrolled Resource Consumption Vulnerability

## Summary
Severity: High
Advisory: GHSA-w6qf-42m7-vh68
CVE: CVE-2024-1635
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-20
Source: https://github.com/advisories/GHSA-w6qf-42m7-vh68
Type: github-advisory

## Affected
- Maven: `io.undertow:undertow-core` — affected >=2.3.0.Final <2.3.12.Final
- Maven: `io.undertow:undertow-core` — affected >=0 <2.2.31.Final

## Details
A vulnerability was found in Undertow. This vulnerability impacts a server that supports the wildfly-http-client protocol. Whenever a malicious user opens and closes a connection with the HTTP port of the server and then closes the connection immediately, the server will end with both memory and open file limits exhausted at some point, depending on the amount of memory available. 

At HTTP upgrade to remoting, the WriteTimeoutStreamSinkConduit leaks connections if RemotingConnection is closed by Remoting ServerConnectionOpenListener. Because the remoting connection originates in Undertow as part of the HTTP upgrade, there is an external layer to the remoting connection. This connection is unaware of the outermost layer when closing the connection during the connection opening procedure. Hence, the Undertow WriteTimeoutStreamSinkConduit is not notified of the closed connection in this scenario. Because WriteTimeoutStreamSinkConduit creates a timeout task, the whole dependency tree leaks via that task, which is added to XNIO WorkerThread. So, the workerThread points to the Undertow conduit, which contains the connections and causes the leak.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1635
- https://github.com/undertow-io/undertow/commit/7d388c5aae9b82afb63f24e3b6a2044838dfb4de
- https://github.com/undertow-io/undertow/commit/3cdb104e225f34547ce9fd6eb8799eb68e040f19
- https://security.netapp.com/advisory/ntap-20240322-0007
- https://github.com/undertow-io/undertow
- https://bugzilla.redhat.com/show_bug.cgi?id=2264928
- https://access.redhat.com/security/cve/CVE-2024-1635
- https://access.redhat.com/errata/RHSA-2025:4226
- https://access.redhat.com/errata/RHSA-2024:4884
- https://access.redhat.com/errata/RHSA-2024:3354
- https://access.redhat.com/errata/RHSA-2024:1866
- https://access.redhat.com/errata/RHSA-2024:1864
- https://access.redhat.com/errata/RHSA-2024:1862
- https://access.redhat.com/errata/RHSA-2024:1861
- https://access.redhat.com/errata/RHSA-2024:1860
- https://access.redhat.com/errata/RHSA-2024:1677
- https://access.redhat.com/errata/RHSA-2024:1676
- https://access.redhat.com/errata/RHSA-2024:1675
- https://access.redhat.com/errata/RHSA-2024:1674
