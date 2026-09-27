# [H] OpenMetadata before 2.0.0 JWT Disclosure via Unvalidated SAML and OIDC Redirect URI

## Summary
Severity: High
Advisory: CVE-2026-81029
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-81029
Type: osv

## Details
OpenMetadata accepts a caller-supplied post-authentication redirect target and appends the issued token to it. SamlLoginServlet reads the callback request parameter and stores it in the HTTP session without comparing it against any configured or registered destination, and the assertion consumer servlet later formats that stored value into a URL carrying the freshly issued JWT together with the account's email and name before sending the redirect. The OIDC and OAuth2 handler follows the same pattern with its own redirect parameter and the issued identity token. A request naming a destination the attacker controls therefore causes the server to deliver a valid token for whoever completes the login to that destination. Because the token authenticates API calls as that account, a user who follows such a link and authenticates hands over control of their account. Version 2.0.0 removes the caller-supplied callback parameter; no 1.x release validates it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81029.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-81029
- https://www.vulncheck.com/advisories/openmetadata-before-2.0.0-jwt-disclosure-via-unvalidated-saml-and-oidc-redirect-uri
- https://github.com/open-metadata/OpenMetadata/issues/29662
- https://github.com/open-metadata/OpenMetadata
- https://github.com/open-metadata/OpenMetadata/blob/1.12.1/openmetadata-service/src/main/java/org/openmetadata/service/security/saml/SamlLoginServlet.java
