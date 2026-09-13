# [H] Keycloak SAML javascript protocol mapper: Uploading of scripts through admin console

## Summary
Severity: High
Advisory: GHSA-wf7g-7h6h-678v
CVE: CVE-2022-2668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-23
Source: https://github.com/advisories/GHSA-wf7g-7h6h-678v
Type: github-advisory

## Affected
- Maven: `org.keycloak:keycloak-parent` — affected >=0 <19.0.2

## Details
An issue was discovered in Keycloak allows arbitrary Javascript to be uploaded for the SAML protocol mapper even if the `UPLOAD_SCRIPTS` feature is disabled

## References
- https://github.com/keycloak/keycloak/security/advisories/GHSA-wf7g-7h6h-678v
- https://nvd.nist.gov/vuln/detail/CVE-2022-2668
- https://github.com/keycloak/keycloak/commit/e2ae7eef39b27e48ffa4764995d558555f02838c
- https://access.redhat.com/security/cve/CVE-2022-2668
- https://bugzilla.redhat.com/show_bug.cgi?id=2115392
- https://github.com/keycloak/keycloak
