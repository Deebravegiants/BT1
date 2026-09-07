# [M] IdentityServer Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-55p7-v223-x366
CWE: CWE-601
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-31
Source: https://github.com/advisories/GHSA-55p7-v223-x366
Type: github-advisory

## Affected
- NuGet: `IdentityServer4` — affected >=0

## Details
### Impact
It is possible for an attacker to craft malicious Urls that certain functions in IdentityServer will incorrectly treat as local and trusted. If such a Url is returned as a redirect, some browsers will follow it to a third-party, untrusted site.

### Affected Methods
- In the `DefaultIdentityServerInteractionService`, the `GetAuthorizationContextAsync` method may return non-null and the `IsValidReturnUrl` method may return true for malicious Urls, indicating incorrectly that they can be safely redirected to.

   _UI code calling these two methods is the most commonly used code path that will expose the vulnerability. The default UI templates rely on this behavior in the Login, Challenge, and Consent pages. Customized user interface code might also rely on this behavior. The following uncommonly used APIs are also vulnerable:_

- The `ServerUrlExtensions.GetIdentityServerRelativeUrl`, `ReturnUrlParser.ParseAsync` and `OidcReturnUrlParser.ParseAsync`  methods may incorrectly return non-null, and the `ReturnUrlParser.IsValidReturnUrl` and `OidcReturnUrlParser.IsValidReturnUrl` methods may incorrectly return true for malicious Urls.

### Patches
IdentityServer4 is no longer supported and will not be receiving updates. Please consider updating to [Duende.IdentityServer](https://duendesoftware.com).

## References
- https://github.com/DuendeSoftware/IdentityServer/security/advisories/GHSA-ff4q-64jc-gx98
- https://github.com/IdentityServer/IdentityServer4/security/advisories/GHSA-55p7-v223-x366
- https://nvd.nist.gov/vuln/detail/CVE-2024-39694
- https://github.com/IdentityServer/IdentityServer4
