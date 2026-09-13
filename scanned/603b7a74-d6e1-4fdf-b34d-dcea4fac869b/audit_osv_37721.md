# [H] EVerest: MQTT Switch-Phases Command Data Race Causing Charger State Corruptio

## Summary
Severity: High
Advisory: CVE-2026-33009
Aliases: GHSA-33qh-fg6f-jjx5
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-33009
Type: osv

## Details
EVerest is an EV charging software stack. Versions prior to 2026.02.0 have a data race leading to C++ UB (potential memory corruption). This is triggered by an MQTT `everest_external/nodered/{connector}/cmd/switch_three_phases_while_charging` message and results in `Charger::shared_context` / `internal_context` accessed concurrently without lock. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33009.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-33qh-fg6f-jjx5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33009
