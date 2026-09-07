# [H] CoreWCF: SAML SubjectConfirmation methods and holder-of-key proof keys are not enforced

## Summary
Severity: High
Advisory: GHSA-48pq-2xq3-c2m4
CVE: CVE-2026-54781
CWE: CWE-287, CWE-345
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-48pq-2xq3-c2m4
Type: github-advisory

## Affected
- NuGet: `CoreWCF.Primitives` — affected >=0 <1.8.1
- NuGet: `CoreWCF.Primitives` — affected >=1.9.0 <1.9.1

## Details
### Impact
The relying application is given a ClaimsPrincipal for a subject whose authority over the assertion the sender never proved. There are two distinct exploit shapes:
- Holder-of-key downgrade. An attacker who obtains a holder-of-key SAML assertion that was issued without KeyInfo (issuer bug, custom STS shape, or assertion captured from an interaction where KeyInfo was elided) can present it to the service and be authenticated as the assertion’s subject without producing the proof key the assertion’s confirmation method would normally require. The service’s reliance on holder-of-key for sensitive actions is bypassed.
- Custom-method bypass. An attacker who can obtain or arrange the issuance of a SAML assertion bearing a non-standard confirmation method URI (a permissive STS that accepts arbitrary method strings, an experimental custom IDP, or an attacker-side construction that the issuer signs without validating the method field) can present the assertion and be authenticated. Per-method policies that an application or a binding-level policy expects the framework to enforce are silently bypassed.

#### Preconditions
The service is configured to accept SAML 1.1 tokens via federation. Typical bindings are WS2007FederationHttpBinding and WSFederationHttpBinding, or any custom binding using IssuedSecurityTokenParameters with a SAML 1.1 token type.  
The attacker has obtained at least one signed SAML 1.1 assertion of a shape that triggers the bypass.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
To exploit this issue, it's required that a trusted STS issues SAML assertions whose SubjectConfirmationMethod is not one of the SAML 1.1 trio, or is willing to issue holder-of-key assertions without KeyInfo. If no trusted STS is willing to issue SAML assertions meeting either of these criteria, then a service isn't vulnerable.

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-48pq-2xq3-c2m4
- https://github.com/CoreWCF/CoreWCF
