# [H] Sustainsys.Saml2 Insufficient Identity Provider Issuer Validation

## Summary
Severity: High
Advisory: GHSA-fv2h-753j-9g39
CVE: CVE-2023-41890
CWE: CWE-289, CWE-294
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-09-20
Source: https://github.com/advisories/GHSA-fv2h-753j-9g39
Type: github-advisory

## Affected
- NuGet: `Sustainsys.Saml2` — affected >=0 <1.0.3
- NuGet: `Sustainsys.Saml2` — affected >=2.0.0 <2.9.2
- NuGet: `Kentor.AuthServices` — affected >=0

## Details
### Impact
When a response is processed, the issuer of the Identity Provider is not sufficiently validated. This could allow a malicious identity provider to craft a Saml2 response that is processed as if issued by another identity provider. It is also possible for a malicious end user to cause stored state intended for one identity provider to be used when processing the response from another provider.

An application is impacted if they rely on any of these features in their authentication/authorization logic:
* the issuer of the generated identity and claims
* items in the stored request state (AuthenticationProperties)

### Patches
Patched in version 2.9.2 and 1.0.3. All previous versions are vulnerable.

### Workarounds
The `AcsCommandResultCreated` notification can be used to add the validation required if an upgrade to patched packages is not possible.

### References
The patch is linked to https://github.com/Sustainsys/Saml2/issues/712 and https://github.com/Sustainsys/Saml2/issues/713

## References
- https://github.com/Sustainsys/Saml2/security/advisories/GHSA-fv2h-753j-9g39
- https://nvd.nist.gov/vuln/detail/CVE-2023-41890
- https://github.com/Sustainsys/Saml2/issues/712
- https://github.com/Sustainsys/Saml2/issues/713
- https://github.com/Sustainsys/Saml2
