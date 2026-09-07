# [C] OpenAM has pre-auth Reflected XSS in OAuth2 / OIDC response_mode=form_post via state parameter (FormPostResponse.ftl)

## Summary
Severity: Critical
Advisory: GHSA-fq9h-c788-fx73
CVE: CVE-2026-44203
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-fq9h-c788-fx73
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-oauth2` — affected >=13.0.0 <16.1.1

## Details
### Summary

The OAuth 2.0 / OpenID Connect authorization endpoint does not sufficiently sanitize certain user-supplied parameters before incorporating them into the HTML response generated for the `form_post` response mode. This may allow an attacker to inject content into the rendered page in the context of the OpenAM origin.

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-fq9h-c788-fx73
- https://github.com/OpenIdentityPlatform/OpenAM
- https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.1.1
