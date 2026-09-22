# [M] EVerest EvseManager phase-switch path has unsynchronized shared-state access race condition

## Summary
Severity: Medium
Advisory: CVE-2026-27814
Aliases: GHSA-5528-wc53-v557
CVSS: 4.2 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-27814
Type: osv

## Details
EVerest is an EV charging software stack. Versions prior to 2026.02.0 have a data race (C++ UB) triggered by an A 1-phase ↔ 3-phase switch request (`ac_switch_three_phases_while_charging`) during charging/waiting executes concurrently with the state machine loop. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27814.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-5528-wc53-v557
- https://nvd.nist.gov/vuln/detail/CVE-2026-27814
