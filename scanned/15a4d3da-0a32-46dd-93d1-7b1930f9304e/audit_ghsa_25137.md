# [H] Keycloak Oauth Implementation Error

## Summary
Severity: High
Advisory: GHSA-qc72-gfvw-76h7
CVE: CVE-2017-12160
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-qc72-gfvw-76h7
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <3.3.0.Final

## Details
It was found that Keycloak oauth would permit an authenticated resource to obtain an access/refresh token pair from the authentication server, permitting indefinite usage in the case of permission revocation. An attacker on an already compromised resource could use this flaw to grant himself continued permissions and possibly conduct further attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-12160
- https://access.redhat.com/errata/RHSA-2017:2904
- https://access.redhat.com/errata/RHSA-2017:2905
- https://access.redhat.com/errata/RHSA-2017:2906
- https://bugzilla.redhat.com/show_bug.cgi?id=1484154
- https://github.com/keycloak/keycloak
