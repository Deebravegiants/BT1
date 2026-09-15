# [M] Keycloak vulnerable to session takeover with OIDC offline refreshtokens

## Summary
Severity: Medium
Advisory: GHSA-97g8-xfvw-q4hg
CVE: CVE-2022-3916
CWE: CWE-287, CWE-304, CWE-488, CWE-613
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-97g8-xfvw-q4hg
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <20.0.2

## Details
An issue was discovered in Keycloak when using a client with the `offline_access` scope. Reuse of session ids across root and user authentication sessions and a lack of root session validation enabled attackers to resolve a user session attached to a different previously authenticated user.

This issue most affects users of shared computers. Suppose a user logs out of their account (without clearing their cookies) in a mobile app or similar client that includes the `offline_access` scope, and another user authenticates to the application. In that case, it will share the same root session id, and when utilizing the refresh token, they will be issued a token for the original user.

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-97g8-xfvw-q4hg
- https://nvd.nist.gov/vuln/detail/CVE-2022-3916
- https://access.redhat.com/errata/RHSA-2022:8961
- https://access.redhat.com/errata/RHSA-2022:8962
- https://access.redhat.com/errata/RHSA-2022:8963
- https://access.redhat.com/errata/RHSA-2022:8964
- https://access.redhat.com/errata/RHSA-2022:8965
- https://access.redhat.com/errata/RHSA-2023:1043
- https://access.redhat.com/errata/RHSA-2023:1044
- https://access.redhat.com/errata/RHSA-2023:1045
- https://access.redhat.com/errata/RHSA-2023:1047
- https://access.redhat.com/errata/RHSA-2023:1049
- https://access.redhat.com/security/cve/CVE-2022-3916
- https://bugzilla.redhat.com/show_bug.cgi?id=2141404
- https://github.com/keycloak/keycloak
