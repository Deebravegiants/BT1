# [M] Wazuh - NULL Pointer Dereference in inventory_sync DataValue FlatBuffer Handling

## Summary
Severity: Medium
Advisory: CVE-2026-56401
Aliases: GHSA-6hxp-c9x3-qc7p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56401
Type: osv

## Details
Wazuh wazuh-modulesd before 5.0.0-beta3 contains a null pointer dereference vulnerability in inventory_sync FlatBuffer DataValue handling. An enrolled agent can send a verifier-valid DataValue message omitting the optional id field, causing wazuh-modulesd to crash when dereferencing data->id()->string_view() without null validation, resulting in denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56401.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-6hxp-c9x3-qc7p
- https://nvd.nist.gov/vuln/detail/CVE-2026-56401
- https://www.vulncheck.com/advisories/wazuh-null-pointer-dereference-in-inventory-sync-datavalue-flatbuffer-handling
- https://github.com/wazuh/wazuh/commit/3adf4f87942705aa0ceeba1e145c259cc9dcd242
