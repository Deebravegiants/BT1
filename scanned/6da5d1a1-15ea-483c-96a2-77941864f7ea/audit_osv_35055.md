# [H] EVerest vulnerable to null pointer dereference during DC_ChargeLoopRes document deserialization

## Summary
Severity: High
Advisory: CVE-2025-68141
Aliases: GHSA-ph4w-r9q8-vm9h
CVSS: 7.4 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2025-68141
Type: osv

## Details
EVerest is an EV charging software stack. Prior to version 2025.10.0, during the deserialization of a `DC_ChargeLoopRes` message that includes Receipt as well as TaxCosts, the vector `<DetailedTax>tax_costs` in the target `Receipt` structure is accessed out of bounds. This occurs in the method `template <> void convert(const struct iso20_dc_DetailedTaxType& in, datatypes::DetailedTax& out)` which leads to a null pointer dereference and causes the module to terminate. The EVerest processes and all its modules shut down, affecting all EVSE. Version 2025.10.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68141.json
- https://github.com/EVerest/everest-core/security/advisories/GHSA-ph4w-r9q8-vm9h
- https://nvd.nist.gov/vuln/detail/CVE-2025-68141
