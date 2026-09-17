# [M] Subject Confirmation Method not validated in Saml2 Authentication Services for ASP.NET

## Summary
Severity: Medium
Advisory: GHSA-9475-xg6m-j7pw
CVE: CVE-2020-5268
CWE: CWE-303
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2020-04-22
Source: https://github.com/advisories/GHSA-9475-xg6m-j7pw
Type: github-advisory

## Affected
- NuGet: `Sustainsys.Saml2` — affected >=0 <1.0.2
- NuGet: `Sustainsys.Saml2` — affected >=2.0.0 <2.7.0

## Details
### Impact
Saml2 tokens are usually used as bearer tokens - a caller that presents a token is assumed to be the subject of the token. There is also support in the Saml2 protocol for issuing tokens that is tied to a subject through other means, e.g. holder-of-key where possession of a private key must be proved.
The Sustainsys.Saml2 library incorrectly treats all incoming tokens as bearer tokens, even though they have another subject confirmation method specified. This could be used by an attacker that could get access to Saml2 tokens with another subject confirmation method than bearer. The attacker could then use such a tocken to create a log in session.

### Patches
Version 1.0.2 and 2.7.0 are patched.

### Workarounds
Ensure that any IdentityProvider trusted by the Sustainsys.Saml2 SP only issues bearer tokens if the audience matches the Sustainsys.Saml2 SP.

### For more information
If you have any questions or comments about this advisory:
* Comment on #103
* Email us at security@sustainsys.com if you think that there are further security issues.

## References
- https://github.com/Sustainsys/Saml2/security/advisories/GHSA-9475-xg6m-j7pw
- https://nvd.nist.gov/vuln/detail/CVE-2020-5268
- https://github.com/Sustainsys/Saml2/issues/712
- https://github.com/Sustainsys/Saml2/commit/e58e0a1aff2b1ead6aca080b7cdced55ee6d5241
- https://www.nuget.org/packages/Sustainsys.Saml2
