# [M] Apache Storm's Improper Handling of TLS Client Authentication Failure Leads to Anonymous Principal Assignment

## Summary
Severity: Medium
Advisory: GHSA-j2q8-xx3q-8fqh
CVE: CVE-2026-41081
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-j2q8-xx3q-8fqh
Type: github-advisory

## Affected
- Maven: `org.apache.storm:storm-client` — affected >=0 <2.8.7

## Details
Improper Handling of TLS Client Authentication Failure Leading to Anonymous Principal Assignment in Apache Storm

Versions Affected: up to 2.8.7

Description: When TLS transport is enabled in Apache Storm without requiring client certificate authentication (the default configuration), the TlsTransportPlugin assigns a fallback principal (CN=ANONYMOUS) if no client certificate is presented or if certificate verification fails. The underlying SSLPeerUnverifiedException is caught and suppressed rather than rejecting the connection.

This fail-open behavior means an unauthenticated client can establish a TLS connection and receive a valid principal identity. If the configured authorizer (e.g., SimpleACLAuthorizer) does not explicitly deny access to CN=ANONYMOUS, this may result in unauthorized access to Storm services. The condition is logged at debug level only, reducing visibility in production.

Impact: Unauthenticated clients may be assigned a principal identity, potentially bypassing authorization in permissive or misconfigured environments.

Mitigation: Users should upgrade to 2.8.7 in which TLS authentication failures are handled in a fail-closed manner.

Users who cannot upgrade immediately should:
- Enable mandatory client certificate authentication (nimbus.thrift.tls.client.auth.required: true)
- Ensure authorization rules explicitly deny access to CN=ANONYMOUS
- Review all ACL configurations for implicit default-allow behavior

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-41081
- https://github.com/apache/storm
- https://lists.apache.org/thread/plxx5l29dvplk5rwzdcq53rdfl6v4gs8
- http://www.openwall.com/lists/oss-security/2026/04/25/3
