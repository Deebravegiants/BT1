# [M] Keycloak has debug default bind address

## Summary
Severity: Medium
Advisory: GHSA-j4vq-q93m-4683
CVE: CVE-2025-11538
CWE: CWE-1327
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-j4vq-q93m-4683
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-quarkus-dist` — affected >=0 <26.4.4

## Details
A vulnerability exists in Keycloak's server distribution where enabling debug mode (`--debug`) insecurely defaults to binding the Java Debug Wire Protocol (JDWP) port to all network interfaces (`0.0.0.0`). This exposes the debug port to the local network, allowing an attacker on the same network segment to attach a remote debugger and achieve remote code execution within the Keycloak Java virtual machine.

Red Hat evaluates this as a Moderate impact vulnerability due to the requirement of running debug mode and untrusted network. Also, for Red Hat Single Sign-On, this must as well be bound to 0.0.0.0 address, which is not recommended in production scenarios.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-j4vq-q93m-4683
- https://nvd.nist.gov/vuln/detail/CVE-2025-11538
- https://access.redhat.com/errata/RHSA-2025:21370
- https://access.redhat.com/errata/RHSA-2025:21371
- https://access.redhat.com/security/cve/CVE-2025-11538
- https://bugzilla.redhat.com/show_bug.cgi?id=2402622
- https://github.com/keycloak/keycloak
