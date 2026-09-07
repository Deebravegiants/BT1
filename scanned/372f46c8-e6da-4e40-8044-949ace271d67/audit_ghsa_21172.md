# [H] Eclipse Californium denial of service (DoS) via Datagram Transport Layer Security (DTLS) handshake on parameter mismatch

## Summary
Severity: High
Advisory: GHSA-qq3j-44gw-cf6r
CVE: CVE-2022-2576
CWE: CWE-408
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-30
Source: https://github.com/advisories/GHSA-qq3j-44gw-cf6r
Type: github-advisory

## Affected
- Maven: `org.eclipse.californium:californium-core` — affected >=2.0.0 <2.7.3
- Maven: `org.eclipse.californium:californium-core` — affected >=3.0.0 <3.6.0

## Details
In Eclipse Californium versions 2.0.0 to 2.7.2 and 3.0.0-3.5.0 a DTLS resumption handshake falls back to a DTLS full handshake on a parameter mismatch without using a HelloVerifyRequest. Especially, if used with certificate based cipher suites, that results in message amplification (DDoS other peers) and high CPU load (DoS own peer). The misbehavior occurs only with DTLS_VERIFY_PEERS_ON_RESUMPTION_THRESHOLD values larger than 0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-2576
- https://github.com/eclipse-californium/californium/pull/2039
- https://github.com/eclipse-californium/californium/commit/0cc953a1dc071efc960130e229fcb4f8bda7f9df
- https://github.com/eclipse-californium/californium/commit/8373db84b2d07f22c39ffc333ab881dba9401722
- https://bugs.eclipse.org/580018
- https://github.com/eclipse/californium
