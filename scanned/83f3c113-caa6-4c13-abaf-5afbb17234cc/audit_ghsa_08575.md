# [H] epa4all-client has a VAU Signature bypass

## Summary
Severity: High
Advisory: GHSA-g8r3-5hwf-qp96
CVE: CVE-2026-44900
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-g8r3-5hwf-qp96
Type: github-advisory

## Affected
- Maven: `com.oviva.telematik:epa4all-client` — affected >=0 <1.2.1

## Details
### Impact
In SignedPublicKeysTrustValidatorImpl.isTrusted(), the ECDSA signature verification at line 45 discards the boolean return value of Signature.verify(). The method performs certificate chain validation, OCSP check, and signature algorithm setup, but never checks whether the signature actually matches. For any structurally valid signature, it returns true.

### Patches
Patched in [#34](https://github.com/oviva-ag/epa4all-client/pull/34).

### Workarounds
None.

### Resources
- [MS-OVIVA-EPA4ALL-d76aec](https://www.machinespirits.com/advisory/d76aec/)

### Credits

[Machine Spirits](https://machinespirits.com) (contact@machinespirits.de)
- Dr. rer. nat. Simon Weber
- Dipl.-Inf. Volker Schönefeld
- Chiara Fliegner

## References
- https://github.com/oviva-ag/epa4all-client/security/advisories/GHSA-g8r3-5hwf-qp96
- https://nvd.nist.gov/vuln/detail/CVE-2026-44900
- https://github.com/oviva-ag/epa4all-client/pull/34
- https://github.com/oviva-ag/epa4all-client
- https://www.machinespirits.com/advisory/d76aec
