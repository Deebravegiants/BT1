# [H] CryptoLib Has Out-of-Bounds Write in Crypto_Config_Add_Gvcid_Managed_Parameters

## Summary
Severity: High
Advisory: CVE-2026-21897
Aliases: GHSA-9x7j-gx23-7m5r
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-01-10
Source: https://osv.dev/vulnerability/CVE-2026-21897
Type: osv

## Details
CryptoLib provides a software-only solution using the CCSDS Space Data Link Security Protocol - Extended Procedures (SDLS-EP) to secure communications between a spacecraft running the core Flight System (cFS) and a ground station. Prior to version 1.4.3, the Crypto_Config_Add_Gvcid_Managed_Parameters function only checks whether gvcid_counter > GVCID_MAN_PARAM_SIZE. As a result, it allows up to the 251st entry, which causes a write past the end of the array, overwriting gvcid_counter located immediately after gvcid_managed_parameters_array[250]. This leads to an out-of-bounds write, and the overwritten gvcid_counter may become an arbitrary value, potentially affecting the parameter lookup/registration logic that relies on it. This issue has been patched in version 1.4.3.

## References
- https://github.com/nasa/CryptoLib/releases/tag/v1.4.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21897.json
- https://github.com/nasa/CryptoLib/security/advisories/GHSA-9x7j-gx23-7m5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-21897
