# [M] Keycloak vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-jh7q-5mwf-qvhw
CVE: CVE-2020-10770
CWE: CWE-601, CWE-918
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-jh7q-5mwf-qvhw
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-core` — affected >=0 <13.0.0

## Details
A flaw was found in Keycloak before 13.0.0, where it is possible to force the server to call out an unverified URL using the OIDC parameter `request_uri`. This flaw allows an attacker to use this parameter to execute a Server-side request forgery (SSRF) attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-10770
- https://github.com/keycloak/keycloak-documentation/pull/1086
- https://github.com/keycloak/keycloak/pull/7714
- https://bugzilla.redhat.com/show_bug.cgi?id=1846270
- https://github.com/keycloak/keycloak
- https://issues.redhat.com/browse/KEYCLOAK-14019
- https://issues.redhat.com/browse/KEYCLOAK-3426
- http://packetstormsecurity.com/files/164499/Keycloak-12.0.1-Server-Side-Request-Forgery.html
