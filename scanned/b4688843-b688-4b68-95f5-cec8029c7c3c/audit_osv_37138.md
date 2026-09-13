# [C] arduino-TuyaOpen WiFiMulti Single-Byte Buffer Overflow Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-28520
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-15
Source: https://osv.dev/vulnerability/CVE-2026-28520
Type: osv

## Details
arduino-TuyaOpen before version 1.2.1 contains a single-byte buffer overflow vulnerability in the WiFiMulti component. When the victim's smart hardware connects to an attacker-controlled AP hotspot, the attacker can exploit the overflow to execute arbitrary code on the affected embedded device.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28520.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-28520
- https://src.tuya.com/announcement/32
- https://www.vulncheck.com/advisories/arduino-tuyaopen-wifimulti-single-byte-buffer-overflow-remote-code-execution
- https://github.com/tuya/arduino-TuyaOpen
