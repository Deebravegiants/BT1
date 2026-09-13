# [H] EVerest has OOB via EVSE ID Indexing Mismatch in OCPP 2.0.1 UpdateAllowedEnergyTransferModes

## Summary
Severity: High
Advisory: CVE-2026-26008
Aliases: GHSA-vw95-6jj7-3fv9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-26008
Type: osv

## Details
EVerest is an EV charging software stack. Versions prior to 2026.02.0 have an out-of-bounds access (std::vector) that leads to possible remote crash/memory corruption. This is because the CSMS sends UpdateAllowedEnergyTransferModes over the network. Version 2026.2.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26008.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-vw95-6jj7-3fv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-26008
