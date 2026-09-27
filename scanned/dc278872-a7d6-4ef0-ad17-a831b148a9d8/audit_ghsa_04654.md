# [C] CoreWCF: Authentication bypass in CoreWCF SAML 1.1 / 2.0 token signature validation

## Summary
Severity: Critical
Advisory: GHSA-xjr9-gg9q-jx3v
CVE: CVE-2026-54782
CWE: CWE-290, CWE-347
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-xjr9-gg9q-jx3v
Type: github-advisory

## Affected
- NuGet: `CoreWCF.Primitives` — affected >=0 <1.8.1
- NuGet: `CoreWCF.Primitives` — affected >=1.9.0 <1.9.1

## Details
### Impact
Full impersonation of any principal the trusted STS could have issued an assertion for — including administrative principals when the relying party grants them via SAML claims. Affects both SAML 1.1 and SAML 2.0.

#### Preconditions
Relying-party service is hosted with WSFederationHttpBinding or WS2007FederationHttpBinding (or any binding that triggers FederatedSecurityTokenManager for issued-token validation), and IdentityConfiguration is wired (UseIdentityConfiguration = true).
Attacker can reach the service over the network and knows the trusted STS’s public certificate (public certs are by design discoverable).

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
None

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-xjr9-gg9q-jx3v
- https://github.com/CoreWCF/CoreWCF
