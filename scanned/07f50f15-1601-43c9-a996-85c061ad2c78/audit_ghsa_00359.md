# [C] Apache Qpid Broker vulnerable to authentication port spoofing

## Summary
Severity: Critical
Advisory: GHSA-269m-695x-j34p
CVE: CVE-2017-15702
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-19
Source: https://github.com/advisories/GHSA-269m-695x-j34p
Type: github-advisory

## Affected
- Maven: `org.apache.qpid:qpid-broker` — affected >=0.18 <6.0.0

## Details
Apache Qpid Broker-J versions 0.18 through 0.32 are vulnerable to authentication port spoofing. When the broker is configured with different authentication providers on different ports, one of which is an HTTP port, then the broker can be tricked by a remote unauthenticated attacker connecting to the HTTP port into using an authentication provider that was configured on a different port. The attacker still needs valid credentials with the authentication provider on the spoofed port. This becomes an issue when the spoofed port has weaker authentication protection (e.g., anonymous access, default accounts) and is normally protected by firewall rules or similar which can be circumvented by this vulnerability. AMQP ports are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15702
- https://github.com/advisories/GHSA-269m-695x-j34p
- https://github.com/apache/qpid-broker-j
- https://issues.apache.org/jira/browse/QPID-8039
- https://lists.apache.org/thread.html/59d241e30db23b8b0af26bb273f789aa1f08515d3dc1a3868d3ba090@%3Cdev.qpid.apache.org%3E
- https://qpid.apache.org/cves/CVE-2017-15702.html
- http://www.securityfocus.com/bid/102040
