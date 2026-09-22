# [M] EVerest: ISO15118 session_setup payment options overflow can corrupt EVSE state

## Summary
Severity: Medium
Advisory: CVE-2026-27815
Aliases: GHSA-7wmg-crc8-6xxf
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-27815
Type: osv

## Details
EVerest is an EV charging software stack. Prior to versions to 2026.02.0, ISO15118_chargerImpl::handle_session_setup copies a variable-length payment_options list into a fixed-size array of length 2 without bounds checking. With schema validation disabled by default, oversized MQTT Cmd payloads can trigger out-of-bounds writes and corrupt adjacent EVSE state or crash the process. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27815.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-7wmg-crc8-6xxf
- https://nvd.nist.gov/vuln/detail/CVE-2026-27815
