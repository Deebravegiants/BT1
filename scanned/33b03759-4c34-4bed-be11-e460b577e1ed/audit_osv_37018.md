# [M] EVerest has use-after-free in auth timeout timer via race condition

## Summary
Severity: Medium
Advisory: CVE-2026-27813
Aliases: GHSA-vgmh-mmg3-22m6
CVSS: 5.3 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-03-26
Source: https://osv.dev/vulnerability/CVE-2026-27813
Type: osv

## Details
EVerest is an EV charging software stack. Versions prior to 2026.02.0 have a data race leading to use-after-free. This is triggered by EV plug-in/unplug and RFID/RemoteStart/OCPP authorization events (or delayed authorization response). Version 2026.2.0 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27813.json
- https://github.com/EVerest/EVerest/security/advisories/GHSA-vgmh-mmg3-22m6
- https://nvd.nist.gov/vuln/detail/CVE-2026-27813
