# [M] arduino-TuyaOpen WiFiUDP Null Pointer Dereference Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-28522
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-15
Source: https://osv.dev/vulnerability/CVE-2026-28522
Type: osv

## Details
arduino-TuyaOpen before version 1.2.1 contains a null pointer dereference vulnerability in the WiFiUDP component. An attacker on the same local area network can send a large volume of malicious UDP packets that trigger a null pointer dereference, resulting in a denial-of-service condition.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28522.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28522
- https://src.tuya.com/announcement/32
- https://www.vulncheck.com/advisories/arduino-tuyaopen-wifiudp-null-pointer-dereference-denial-of-service
- https://github.com/tuya/arduino-TuyaOpen
