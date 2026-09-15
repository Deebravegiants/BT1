# [H] CoreWCF: SPNEGO SecurityContextToken proof key wrapped without confidentiality

## Summary
Severity: High
Advisory: GHSA-2288-8h3r-cqgg
CVE: CVE-2026-54784
CWE: CWE-311, CWE-523
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-2288-8h3r-cqgg
Type: github-advisory

## Affected
- NuGet: `CoreWCF.Primitives` — affected >=1.9.0 <1.9.1

## Details
### Impact
When the proof key recovered from the RSTR can be observed by a party that is not the legitimate client, that party can impersonate the authenticated Windows principal for the lifetime of the SCT (default ~10 hours) and decrypt or forge any subsequent WS‑SecureConversation traffic that uses keys derived from the SCT.

#### Preconditions
Using security mode TransportWithMessageCredential with client credential type Windows, along with session establishment (which triggers use of WS-SecureConversation).

### Patches
Fixed in CoreWCF v1.9.1

### Workarounds
Ensure communication is protected by SSL/TLS to prevent capturing of SCT negotiation handshake.

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-2288-8h3r-cqgg
- https://github.com/CoreWCF/CoreWCF
