# [M] Logto Server-Side Request Forgery via OIDC SSO Connector Issuer URL

## Summary
Severity: Medium
Advisory: CVE-2026-82263
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82263
Type: osv

## Details
Logto through 1.42.0 contains a server-side request forgery vulnerability in the OIDC SSO connector creation endpoint that fails to validate the issuer URL parameter. Tenant administrators with Management API credentials can supply arbitrary internal URLs to trigger HTTP GET requests to private network services, with response content returned in API responses.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82263.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-82263
- https://www.vulncheck.com/advisories/logto-server-side-request-forgery-via-oidc-sso-connector-issuer-url
- https://github.com/logto-io/logto/issues/9465
- https://github.com/logto-io/logto/commit/16f4b2e732d5114ac98646c9370ec6ab61d6ed26
- https://github.com/logto-io/logto
- https://github.com/logto-io/logto/blob/v1.42.0/packages/core/src/sso/OidcConnector/utils.ts
