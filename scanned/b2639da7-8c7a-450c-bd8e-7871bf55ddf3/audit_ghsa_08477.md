# [H] Improper Verification of Cryptographic Signature in com.oviva.telematik:epa4all-client

## Summary
Severity: High
Advisory: GHSA-gqx7-6552-67hf
CVE: CVE-2026-45575
CWE: CWE-347
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-gqx7-6552-67hf
Type: github-advisory

## Affected
- Maven: `com.oviva.telematik:epa4all-client` — affected >=0 <1.2.2

## Details
### Impact
An attacker who can MITM the TLS connection between the client and the IDP (within the TI network) can substitute a forged discovery document. The forged document redirects u ri_puk_idp_enc and uri_puk_idp_sig to attacker-controlled URLs. The client then encrypts the SMC-B-signed challenge response to the attacker's encryption key and POSTs it to the attacker's auth endpoint. This captures the signed authentication material.

### Patches
[#36](https://github.com/oviva-ag/epa4all-client/pull/36)

### Workarounds
None.

### Resources
- MS-OVIVA-EPA4ALL-d453c1

### Credits
[Machine Spirits](https://machinespirits.com/) ([contact@machinespirits.de](mailto:contact@machinespirits.de))

- Dr. rer. nat. Simon Weber
- Dipl.-Inf. Volker Schönefeld
- Chiara Fliegner

## References
- https://github.com/oviva-ag/epa4all-client/security/advisories/GHSA-gqx7-6552-67hf
- https://nvd.nist.gov/vuln/detail/CVE-2026-45575
- https://github.com/oviva-ag/epa4all-client/pull/36
- https://github.com/oviva-ag/epa4all-client/commit/9111d6fbb939007036a7f74b2a93bb278cb5af32
- https://github.com/oviva-ag/epa4all-client
- https://github.com/oviva-ag/epa4all-client/releases/tag/v1.2.2
