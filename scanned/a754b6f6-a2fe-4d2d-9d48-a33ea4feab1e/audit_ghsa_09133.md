# [H] Keycloak: Denial of Service via specially crafted SAML input

## Summary
Severity: High
Advisory: GHSA-p5mv-gj8j-xqgf
CVE: CVE-2026-7307
CWE: CWE-1286
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-p5mv-gj8j-xqgf
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-saml-core` — affected >=0 <26.6.2

## Details
A flaw was found in Keycloak. A remote, unauthenticated attacker can send a specially crafted XML input to the Security Assertion Markup Language (SAML) endpoint. This malicious input can cause high CPU usage and worker thread starvation, leading to a Denial of Service (DoS) where the server becomes unavailable.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7307
- https://github.com/keycloak/keycloak/pull/49119
- https://github.com/keycloak/keycloak/commit/be84d28ce4c69c038d542f11405d5ede1d61f4a9
- https://access.redhat.com/errata/RHSA-2026:19594
- https://access.redhat.com/errata/RHSA-2026:19595
- https://access.redhat.com/errata/RHSA-2026:19596
- https://access.redhat.com/errata/RHSA-2026:19597
- https://access.redhat.com/security/cve/CVE-2026-7307
- https://bugzilla.redhat.com/show_bug.cgi?id=2476526
- https://github.com/keycloak/keycloak
- https://github.com/keycloak/keycloak/releases/tag/26.6.2
