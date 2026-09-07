# [H] epa4all-client: TLS Certificate Validation Disabled in Production

## Summary
Severity: High
Advisory: GHSA-5hhf-xmfx-4vvr
CVE: CVE-2026-45574
CWE: CWE-295
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-15
Source: https://github.com/advisories/GHSA-5hhf-xmfx-4vvr
Type: github-advisory

## Affected
- Maven: `com.oviva.telematik:epa4all-client` — affected >=0 <1.2.2

## Details
### Impact
An attacker on the network path between the ePA service and the Konnektor can present any TLS certificate (self-signed, expired, wrong CN) and intercept all SOAP traffic. This includes patient identifiers (KVNR), SMC-B card operations (authentication, signing),
document content, and credential exchanges.

### Patches
[#36](https://github.com/oviva-ag/epa4all-client/pull/36)

### Workarounds
Use the library directly instead of the REST wrapper.

### Resources
- MS-OVIVA-EPA4ALL-771a78

### Credits
[Machine Spirits](https://machinespirits.com/) ([contact@machinespirits.de](mailto:contact@machinespirits.de))

- Dr. rer. nat. Simon Weber
- Dipl.-Inf. Volker Schönefeld
- Chiara Fliegner

## References
- https://github.com/oviva-ag/epa4all-client/security/advisories/GHSA-5hhf-xmfx-4vvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-45574
- https://github.com/oviva-ag/epa4all-client/pull/36
- https://github.com/oviva-ag/epa4all-client/commit/9111d6fbb939007036a7f74b2a93bb278cb5af32
- https://github.com/oviva-ag/epa4all-client
- https://github.com/oviva-ag/epa4all-client/releases/tag/v1.2.2
