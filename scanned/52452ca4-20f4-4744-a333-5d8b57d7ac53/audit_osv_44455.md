# [H] pac4j-oidc before 6.5.6 Privilege Escalation via Unverified Keycloak Access Token

## Summary
Severity: High
Advisory: CVE-2026-82461
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82461
Type: osv

## Details
pac4j-oidc before 6.5.6 fails to verify access token signatures, issuers, audiences, or expiry when extracting Keycloak realm and client roles. Attackers can forge access tokens with administrative roles paired with valid ID tokens to bypass authorization checks in applications relying on pac4j role validation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82461.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82461
- https://www.pac4j.org/blog/security-advisory-pac4j-core-oidc-saml.html
- https://www.vulncheck.com/advisories/pac4j-oidc-before-6.5.6-privilege-escalation-via-unverified-keycloak-access-token
- https://github.com/pac4j/pac4j/commit/2270c3ff70e93cc43831e75702acd5135531237e
- https://github.com/pac4j/pac4j
- https://github.com/pac4j/pac4j/blob/pac4j-parent-6.5.5/pac4j-oidc/src/main/java/org/pac4j/oidc/authorization/generator/KeycloakRolesAuthorizationGenerator.java
