# [H] EVerest: OCPP201 startup event_queue lock mismatch leads to std::map/std::queue data race

## Summary
Severity: High
Advisory: CVE-2026-26074
Aliases: GHSA-p3hg-vqgv-h524
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-26074
Type: osv

## Details
EVerest is an EV charging software stack. Versions prior to 2026.02.0 have a data race leading to possible `std::map<std::queue>` corruption. The trigger is CSMS GetLog/UpdateFirmware request (network) with an EVSE fault event (physical). This results in TSAN reports concurrent access (data race) to `event_queue`. Version 2026.2.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26074.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-p3hg-vqgv-h524
- https://nvd.nist.gov/vuln/detail/CVE-2026-26074
