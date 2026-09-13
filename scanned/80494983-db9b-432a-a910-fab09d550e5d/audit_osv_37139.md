# [H] arduino-TuyaOpen TuyaIoT Out-of-Bounds Memory Read Information Disclosure

## Summary
Severity: High
Advisory: CVE-2026-28521
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-15
Source: https://osv.dev/vulnerability/CVE-2026-28521
Type: osv

## Details
arduino-TuyaOpen before version 1.2.1 contains an out-of-bounds memory read vulnerability in the TuyaIoT component. An attacker who hijacks or controls the Tuya cloud service can issue malicious DP event data to victim devices, causing out-of-bounds memory access that may result in information disclosure or a denial-of-service condition.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28521.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28521
- https://src.tuya.com/announcement/32
- https://www.vulncheck.com/advisories/arduino-tuyaopen-tuyaiot-out-of-bounds-memory-read-information-disclosure
- https://github.com/tuya/arduino-TuyaOpen
