# [M] Duende.AccessTokenManagement race condition when concurrently retrieving customized Client Credentials Access Tokens

## Summary
Severity: Medium
Advisory: GHSA-qxj7-2x7w-3mpp
CVE: CVE-2025-26620
CWE: CWE-367
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2025-02-19
Source: https://github.com/advisories/GHSA-qxj7-2x7w-3mpp
Type: github-advisory

## Affected
- NuGet: `Duende.AccessTokenManagement` — affected >=0 <3.2.0

## Details
### Summary
Duende.AccessTokenManagement contains a race condition when requesting access tokens using the client credentials flow. Concurrent requests to obtain an access token using differing protocol parameters can return access tokens obtained with the wrong scope, resource indicator, or other protocol parameters. Such usage is somewhat atypical, and only a small percentage of users are likely to be affected.

### Details
Duende.AccessTokenManagement can request access tokens using the client credentials flow in several ways. In basic usage, the client credentials flow is configured once and the parameters do not vary. In more advanced situations, requests with varying protocol parameters may be made by calling specific overloads of these methods:

- `HttpContext.GetClientAccessTokenAsync()`
- `IClientCredentialsTokenManagementService.GetAccessTokenAsync()`

There are overloads of both of these methods that accept a `TokenRequestParameters` object that customizes token request parameters. However, concurrent requests with varying `TokenRequestParameters` will result in the same token for all concurrent calls.


### Upgrading
Most users can simply update the NuGet package to the latest version. Customizations of the `IClientCredentialsTokenCache` that derive from the default implementation (`DistributedClientCredentialsTokenCache`) will require a small code change, as its constructor was changed to add a dependency on the `ITokenRequestSynchronization` service. The synchronization service will need to be injected into the derived class and passed to the base constructor.

### Impact
The impact of this vulnerability depends on how Duende.AccessTokenManagement is used and on the security architecture of the solution. Most users will not be vulnerable to this issue. More advanced users may run into this issue by calling the methods specified above with customized token request parameters. The impact of obtaining an access token with different than intended protocol parameters will vary depending on application logic, security architecture, and the authorization policy of the resource servers.

Thank you to **Michael Dimoudis** of **PageUp** for finding this issue and responsibly disclosing it!

## References
- https://github.com/DuendeSoftware/foss/security/advisories/GHSA-qxj7-2x7w-3mpp
- https://nvd.nist.gov/vuln/detail/CVE-2025-26620
- https://github.com/DuendeSoftware/foss/commit/a33332ddec0ebf3c048ba85427e3c77d47c68dac
- https://github.com/DuendeSoftware/foss
