# [H] CVE-2026-37231

## Summary
Severity: High
Advisory: CVE-2026-37231
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-37231
Type: osv

## Details
FlexRIC v2.0.0 uses a uint16_t counter for xapp_id assignment but stores the value in uint32_t message fields. After 65,530+ E42_SETUP_REQUESTs, the 16-bit counter wraps around and produces duplicate xapp_ids. The iApp (port 36422) crashes when attempting to register a duplicate ID in its internal data structure. A remote attacker can trigger this by repeatedly connecting and requesting new xApp registrations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/37xxx/CVE-2026-37231.json
- https://github.com/MinamiKotor1/oran-security-advisories-zhongnan-luo/blob/main/advisories/CVE-2026-37231.md
- https://nvd.nist.gov/vuln/detail/CVE-2026-37231
- https://gitlab.eurecom.fr/mosaic5g/flexric
