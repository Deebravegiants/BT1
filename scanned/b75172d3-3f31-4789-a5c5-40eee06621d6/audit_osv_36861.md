# [M] EVerest: OCPP 2.0.1 EVCCID Data Race Leads to Heap Use‑After‑Free

## Summary
Severity: Medium
Advisory: CVE-2026-26071
Aliases: GHSA-xww8-4hfx-9fjw
CVSS: 4.2 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-26071
Type: osv

## Details
EVerest is an EV charging software stack. Versions prior to 2026.02.0 have a data race leading to `std::string` concurrent access. with heap-use-after-free possible. This is triggered by EVCCID update (EV/ISO15118) and OCPP session/authorization events. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26071.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-xww8-4hfx-9fjw
- https://nvd.nist.gov/vuln/detail/CVE-2026-26071
