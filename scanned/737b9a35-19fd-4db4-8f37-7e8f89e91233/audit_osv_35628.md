# [M] Caliptra Update-Reset Secure-Boot Bypass via Attacker-Chosen AXI Staging Address (TOCTOU)

## Summary
Severity: Medium
Advisory: CVE-2026-11835
Aliases: GHSA-49mm-5gq5-v97f
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:P/PR:H/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-11835
Type: osv

## Details
Time-of-check time-of-use (TOCTOU) vulnerability combined with missing input validation in Caliptra Core ROM (UpdateResetFlow::run()) in subsystem mode allows a compromised local attacker to silently bypass secure boot by supplying an AXI staging address that is not validated against the strap-configured SS_EXTERNAL_STAGING_AREA_BASE_ADDR, enabling firmware to be modified between verification and loading into ICCM. Attestation continues to report the originally verified image digest, masking the compromise. Exploitation requires a compromised MCU firmware with AXI manager access to unprotected SRAM reachable by Caliptra.

This issue affects Core ROM: 2.1.0 through 2.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/11xxx/CVE-2026-11835.json
- https://github.com/chipsalliance/caliptra-sw/security/advisories/GHSA-49mm-5gq5-v97f
- https://nvd.nist.gov/vuln/detail/CVE-2026-11835
- https://github.com/chipsalliance/caliptra-sw
