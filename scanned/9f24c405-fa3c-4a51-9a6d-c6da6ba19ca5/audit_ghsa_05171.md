# [M] CoreWCF: WS-Security signature substitution via document-wide Signature lookup

## Summary
Severity: Medium
Advisory: GHSA-jc6x-rj79-w4mx
CVE: CVE-2026-54773
CWE: CWE-347
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-jc6x-rj79-w4mx
Type: github-advisory

## Affected
- NuGet: `CoreWCF.Primitives` — affected >=0 <1.8.1
- NuGet: `CoreWCF.Primitives` — affected >=1.9.0 <1.9.1

## Details
### Impact
An unauthenticated remote attacker who can place a SOAP header lexically before `wsse:Security` can embed a `ds:Signature` of their choosing inside that header and cause the server to verify the attacker-supplied signature instead of the one carried in the security header.

#### Preconditions
Exploitation requires the endpoint be configured with an endorsing supporting token binding, and the attacker constructs a `ds:Signature` whose `KeyInfo` resolves through the receive-side token resolver to a key under the attacker’s control. Both are conditions outside the attacker’s direct control on a generic deployment.

### Patches
Fixed in CoreWCF v1.8.1 and v1.9.1

### Workarounds
Use a security token resolver that only accepts references to issuer-pinned X.509 chains (the default when expecting a static set of signing certificates).

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-jc6x-rj79-w4mx
- https://github.com/CoreWCF/CoreWCF
