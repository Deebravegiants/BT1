# [H] Auth0-ASPNET and Auth0-ASPNET-Owin vulnerable to Cross-Site Request Forgery

## Summary
Severity: High
Advisory: GHSA-mmhr-3jr7-qj2p
CVE: CVE-2018-15121
CWE: CWE-352
Ecosystem: NuGet
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mmhr-3jr7-qj2p
Type: github-advisory

## Affected
- NuGet: `Auth0-ASPNET-Owin` — affected >=0
- NuGet: `auth0-aspnet` — affected >=0

## Details
An issue was discovered in Auth0 auth0-aspnet and auth0-aspnet-owin. Affected packages do not use or validate the state parameter of the OAuth 2.0 and OpenID Connect protocols. This leaves applications vulnerable to CSRF attacks during authentication and authorization operations.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-15121
- https://auth0.com/docs/security/bulletins/cve-2018-15121
- https://github.com/auth0/auth0-aspnet-owin
- https://www.nuget.org/packages/Auth0-ASPNET-Owin
