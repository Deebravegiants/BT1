# [H] CoreWCF: SamlSerializer skips SignatureValue verification when SAML signing token is not an X.509 certificate

## Summary
Severity: High
Advisory: GHSA-rpj7-hr7h-w6p9
CVE: CVE-2026-54774
CWE: CWE-345, CWE-347
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-rpj7-hr7h-w6p9
Type: github-advisory

## Affected
- NuGet: `CoreWCF.Primitives` — affected >=0 <1.8.1
- NuGet: `CoreWCF.Primitives` — affected >=1.9.0 <1.9.1

## Details
### Impact
When a service is configured to validate SAML tokens using a method other than X.509 certificate signing, the final signature verification is skipped.

#### Preconditions
The service is configured to authenticate using SAML tokens and an out of band token resolver (commonly the IssuerTokenResolver of IssuedTokenServiceCredential) holds a non-X.509 SecurityToken whose key identifier the attacker can reference in the assertion’s `<KeyInfo>` - for example a `BinarySecretSecurityToken` representing the symmetric proof key issued by a WS-Trust symmetric-key holder-of-key STS.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
None

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-rpj7-hr7h-w6p9
- https://github.com/CoreWCF/CoreWCF
