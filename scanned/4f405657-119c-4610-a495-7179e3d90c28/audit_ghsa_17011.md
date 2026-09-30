# [M] Keycloak vulnerable to session hijacking via re-authentication

## Summary
Severity: Medium
Advisory: GHSA-c9h6-v78w-52wj
CVE: CVE-2023-6787
CWE: CWE-287, CWE-384, CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-c9h6-v78w-52wj
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-services` — affected >=0 <22.0.10
- Maven: `org.keycloak:keycloak-services` — affected >=23.0.0 <24.0.3

## Details
A flaw was found in Keycloak. An active keycloak session can be hijacked by initiating a new authentication (having the query parameter prompt=login) and forcing the user to enter his credentials once again. If the user cancels this re-authentication by clicking Restart login, the account takeover could take place as the new session, with a different SUB, will have the same SID as the previous session.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-c9h6-v78w-52wj
- https://nvd.nist.gov/vuln/detail/CVE-2023-6787
- https://access.redhat.com/errata/RHSA-2024:1867
- https://access.redhat.com/errata/RHSA-2024:1868
- https://access.redhat.com/security/cve/CVE-2023-6787
- https://bugzilla.redhat.com/show_bug.cgi?id=2254375
- https://github.com/keycloak/keycloak
