# [M] Keycloak does not invalidate sessions when "Remember Me" is disabled

## Summary
Severity: Medium
Advisory: GHSA-64w3-5q9m-68xf
CVE: CVE-2025-11429
CWE: CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-23
Source: https://github.com/advisories/GHSA-64w3-5q9m-68xf
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=26.3.0 <26.4.1
- Maven: `org.keycloak:keycloak-services` — affected >=0 <26.2.11

## Details
A flaw was found in Keycloak. Keycloak does not immediately enforce the disabling of the "Remember Me" realm setting on existing user sessions. Sessions created while "Remember Me" was active retain their extended session lifetime until they expire, overriding the administrator's recent security configuration change. This is a logic flaw in session management increases the potential window for successful session hijacking or unauthorized long-term access persistence. The flaw lies in the session expiration logic relying on the session-local "remember-me" flag without validating the current realm-level configuration.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-11429
- https://github.com/keycloak/keycloak/issues/43328
- https://github.com/keycloak/keycloak/commit/a34094100716b7c69ae38eaed6678ab4344d0a1d
- https://github.com/keycloak/keycloak/commit/a752492843e21c3ab06090616692e53001864158
- https://github.com/keycloak/keycloak/commit/bda0e2a67c8cf41d1b3d9010e6dfcddaf79bf59b
- https://access.redhat.com/errata/RHSA-2025:22088
- https://access.redhat.com/errata/RHSA-2025:22089
- https://access.redhat.com/security/cve/CVE-2025-11429
- https://bugzilla.redhat.com/show_bug.cgi?id=2402148
- https://github.com/keycloak/keycloak
