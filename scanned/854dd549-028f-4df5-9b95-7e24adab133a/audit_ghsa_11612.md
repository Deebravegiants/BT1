# [C] Apache Artemis and Apache ActiveMQ Artemis are Missing Authentication for Critical Functions

## Summary
Severity: Critical
Advisory: GHSA-fw88-pf9m-p947
CVE: CVE-2026-27446
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-fw88-pf9m-p947
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:artemis-server` — affected >=2.11.0
- Maven: `org.apache.artemis:artemis-server` — affected >=2.50.0 <2.52.0

## Details
Missing Authentication for Critical Function (CWE-306) vulnerability in Apache Artemis, Apache ActiveMQ Artemis. An unauthenticated remote attacker can use the Core protocol to force a target broker to establish an outbound Core federation connection to an attacker-controlled rogue broker. This could potentially result in message injection into any queue and/or message exfiltration from any queue via the rogue broker. This impacts environments that allow both:

- Incoming Core protocol connections from untrusted sources to the broker

- Outgoing Core protocol connections from the broker to untrusted targets

This issue affects:

- Apache Artemis from 2.50.0 through 2.51.0

- Apache ActiveMQ Artemis from 2.11.0 through 2.44.0.

Users are recommended to upgrade to Apache Artemis version 2.52.0, which fixes the issue.

The issue can be mitigated by either of the following:

- Remove Core protocol support from any acceptor receiving connections from untrusted sources. Incoming Core protocol connections are supported by default via the "artemis" acceptor listening on port 61616. See the "protocols" URL parameter configured for the acceptor. An acceptor URL without this parameter supports all protocols by default, including Core.

- Use two-way SSL (i.e. certificate-based authentication) in order to force every client to present the proper SSL certificate when establishing a connection before any message protocol handshake is attempted. This will prevent unauthenticated exploitation of this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27446
- https://cert-portal.siemens.com/productcert/html/ssa-085541.html
- https://github.com/apache/artemis
- https://lists.apache.org/thread/jwpsdc8tdxotm98od8n8n30fqlzoc8gg
- http://www.openwall.com/lists/oss-security/2026/03/03/4
- http://www.openwall.com/lists/oss-security/2026/03/04/1
