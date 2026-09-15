# [H] Keycloak TLS Client-Initiated Renegotiation Denial of Service

## Summary
Severity: High
Advisory: GHSA-q8hq-4h99-fj7x
CVE: CVE-2025-11419
CWE: CWE-400, CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-10-27
Source: https://github.com/advisories/GHSA-q8hq-4h99-fj7x
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-quarkus-dist` — affected >=0 <26.0.16
- Maven: `org.keycloak:keycloak-quarkus-dist` — affected >=26.1.0 <26.2.10
- Maven: `org.keycloak:keycloak-quarkus-dist` — affected >=26.3.0 <26.4.1

## Details
Keycloak is vulnerable to a Denial of Service (DoS) attack due to the default JDK setting that permits Client-Initiated Renegotiation in TLS 1.2. An unauthenticated remote attacker can repeatedly initiate TLS renegotiation requests to exhaust server CPU resources, making the service unavailable. Immediate mitigation is available by setting the `-Djdk.tls.rejectClientInitiatedRenegotiation=true` Java system property in the Keycloak startup configuration.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-q8hq-4h99-fj7x
- https://nvd.nist.gov/vuln/detail/CVE-2025-11419
- https://github.com/keycloak/keycloak/issues/43020
- https://access.redhat.com/errata/RHSA-2025:18254
- https://access.redhat.com/errata/RHSA-2025:18255
- https://access.redhat.com/errata/RHSA-2025:18889
- https://access.redhat.com/errata/RHSA-2025:18890
- https://access.redhat.com/security/cve/CVE-2025-11419
- https://bugzilla.redhat.com/show_bug.cgi?id=2402142
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/discussions/25209
