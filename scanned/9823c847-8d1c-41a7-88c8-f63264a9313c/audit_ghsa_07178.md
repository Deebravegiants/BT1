# [M] Steeltoe's static JWKS cache shared across schemes and never invalidated

## Summary
Severity: Medium
Advisory: GHSA-7fqc-p256-7pwj
CVE: CVE-2026-50202
CWE: CWE-668
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-7fqc-p256-7pwj
Type: github-advisory

## Affected
- NuGet: `Steeltoe.Security.Authentication.JwtBearer` — affected >=0 <4.2.0
- NuGet: `Steeltoe.Security.Authentication.OpenIdConnect` — affected >=0 <4.2.0
- NuGet: `Steeltoe.Security.Authentication.CloudFoundryBase` — affected >=0 <3.4.0

## Details
### Summary

The JWT signing key cache in `TokenKeyResolver` uses `kid` as the sole cache key without namespacing by authority. In applications with multiple `JwtBearer` schemes pointing to different identity providers, a key fetched for one scheme can satisfy token validation for another. Additionally, cached keys have no expiration, so rotated or revoked keys remain trusted until the application process restarts.

### Impact

In multi-scheme deployments, an attacker who controls one identity provider's signing key can forge tokens accepted by other schemes within the same application. For all applications using `TokenKeyResolver`, a signing key removed from the identity provider's JWKS endpoint remains trusted indefinitely.

### Mitigations

If an immediate upgrade is not possible:

- In multi-scheme deployments, configure only one `JwtBearer` scheme per application when different identity providers are required.
- Restart the application process after an identity provider signing key rotation to clear stale cached keys.

## References
- https://github.com/SteeltoeOSS/security-advisories/security/advisories/GHSA-7fqc-p256-7pwj
- https://nvd.nist.gov/vuln/detail/CVE-2026-50202
- https://github.com/SteeltoeOSS/Steeltoe/commit/04db2ace3b806bfe0260bb7d4bda340f241eff48
- https://github.com/SteeltoeOSS/Steeltoe/commit/17b27b8be546ae3f83a2f6e91d45e0c84c5314b7
- https://github.com/SteeltoeOSS/security-advisories
