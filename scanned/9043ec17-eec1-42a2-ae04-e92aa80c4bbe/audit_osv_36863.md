# [M] EVerest: OCPP 1.6 heap corruption caused by lock-free insertion in event_queue

## Summary
Severity: Medium
Advisory: CVE-2026-26073
Aliases: GHSA-jf36-f4f9-7qc2
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-26073
Type: osv

## Details
EVerest is an EV charging software stack. Versions prior to 2026.02.0 have a data race leading to possible `std::queue`/`std::deque` corruption. The trigger is powermeter public key update and EV session/error events (while OCPP not started). This results in a TSAN data race report and an ASAN/UBSAN misaligned address runtime error being observed. Version 2026.02.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26073.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-jf36-f4f9-7qc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-26073
