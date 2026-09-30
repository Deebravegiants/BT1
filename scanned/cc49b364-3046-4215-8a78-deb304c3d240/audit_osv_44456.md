# [H] pac4j-core before 6.5.6 Authorization Bypass via Reversed Profile Type Check

## Summary
Severity: High
Advisory: CVE-2026-82463
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-29
Source: https://osv.dev/vulnerability/CVE-2026-82463
Type: osv

## Details
pac4j-core before 6.5.6 contains an authentication bypass vulnerability in CheckProfileTypeAuthorizer that reverses the profile type validation logic. Attackers can authenticate through a weaker client and access resources requiring a stronger profile type by satisfying generic profile checks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82463.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82463
- https://www.pac4j.org/blog/security-advisory-pac4j-core-oidc-saml.html
- https://www.vulncheck.com/advisories/pac4j-core-before-6.5.6-authorization-bypass-via-reversed-profile-type-check
- https://github.com/pac4j/pac4j/commit/2270c3ff70e93cc43831e75702acd5135531237e
- https://github.com/pac4j/pac4j
- https://github.com/pac4j/pac4j/blob/pac4j-parent-6.5.5/pac4j-core/src/main/java/org/pac4j/core/authorization/authorizer/CheckProfileTypeAuthorizer.java
