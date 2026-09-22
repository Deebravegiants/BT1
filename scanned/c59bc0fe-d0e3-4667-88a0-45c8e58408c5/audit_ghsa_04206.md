# [H] OpenAM has LDAP Injection via `_queryId` Parameter

## Summary
Severity: High
Advisory: GHSA-2vg8-q4c2-5cw3
CVE: CVE-2026-41573
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-22
Source: https://github.com/advisories/GHSA-2vg8-q4c2-5cw3
Type: github-advisory

## Affected
- Maven: `org.openidentityplatform.openam:openam-core-rest` — affected >=0 <16.1.1

## Details
OpenAM (Open Identity Platform) is an open-source IAM platform providing SSO, OAuth2, SAML, and OpenID Connect capabilities. The CREST REST API layer exposes user query endpoints under `/json/{realm}/users`. In `IdentityResourceV1.queryCollection()`, the HTTP query parameter `_queryId` is passed to a `CrestQuery` object with `escapeQueryId` **explicitly set to `false`**, bypassing the escape protection introduced as part of the CVE-2021-29156 fix. The unescaped value flows directly to `DJLDAPv3Repo.getFilter()` where it is concatenated into an LDAP filter string without sanitization, enabling authenticated attackers to inject arbitrary LDAP metacharacters for user enumeration and blind LDAP injection.


## Affected Endpoint

| Endpoint | Auth Required | Injection Parameter |
|----------|--------------|---------------------|
| `GET /openam/json/{realm}/users?_queryId=<INJECTION>` | SSO Token | `_queryId` |
| `GET /openam/json/{realm}/groups?_queryId=<INJECTION>` | SSO Token (TBD) | `_queryId` |

## Background: CVE-2021-29156

CVE-2021-29156 was a pre-authentication LDAP injection in OpenAM's Webfinger endpoint, where user-supplied input reached `DJLDAPv3Repo.getFilter()` unescaped. The fix introduced the `escapeQueryId` flag in `CrestQuery` (defaulting to `true`) and added `Filter.escapeAssertionValue()` in the filter-building path:

## Credit

Discovered by **JD-Security SHENYI Team**

## References
- https://github.com/OpenIdentityPlatform/OpenAM/security/advisories/GHSA-2vg8-q4c2-5cw3
- https://github.com/OpenIdentityPlatform/OpenAM
- https://github.com/OpenIdentityPlatform/OpenAM/releases/tag/16.1.1
- https://github.com/advisories/GHSA-8984-9gww-h52x
