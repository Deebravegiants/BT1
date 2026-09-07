# [M] HTTP Client uses incorrect token after refresh

## Summary
Severity: Medium
Advisory: GHSA-7mr7-4f54-vcx5
CVE: CVE-2024-51987
CWE: CWE-270
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-11-07
Source: https://github.com/advisories/GHSA-7mr7-4f54-vcx5
Type: github-advisory

## Affected
- NuGet: `Duende.AccessTokenManagement.OpenIdConnect` — affected >=3.0.0 <3.0.1

## Details
### Impact
HTTP Clients created by `AddUserAccessTokenHttpClient` may use a different user's access token after a token refresh. This occurs because a refreshed token will be captured in pooled `HttpClient` instances, which may be used by a different user.

### Workarounds
Instead of using `AddUserAccessTokenHttpClient` to create an `HttpClient` that automatically adds a managed token to outgoing requests, you can use the `HttpConext.GetUserAccessTokenAsync` extension method or the `IUserTokenManagementService.GetAccessTokenAsync` method.

### Patches
This issue is fixed in Duende.AccessTokenManagement.OpenIdConnect 3.0.1.

## References
- https://github.com/DuendeSoftware/Duende.AccessTokenManagement/security/advisories/GHSA-7mr7-4f54-vcx5
- https://nvd.nist.gov/vuln/detail/CVE-2024-51987
- https://github.com/DuendeSoftware/Duende.AccessTokenManagement/commit/09c73e32b182da5c6d7b55ec790cb2271cc4b63f
- https://github.com/DuendeSoftware/Duende.AccessTokenManagement
- https://github.com/DuendeSoftware/Duende.AccessTokenManagement/releases/tag/3.0.1
