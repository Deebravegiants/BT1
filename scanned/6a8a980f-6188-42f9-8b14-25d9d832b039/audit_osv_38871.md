# [C] arduino-esp32: Stack buffer overflow in WebServer multipart boundary parsing leads to remote crash potential RCE

## Summary
Severity: Critical
Advisory: CVE-2026-42854
Aliases: GHSA-8cmm-3887-r32j
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-42854
Type: osv

## Details
arduino-esp32 is an Arduino core for the ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6 and ESP32-H2 microcontrollers. Prior to 3.3.8, the WebServer multipart form parser in arduino-esp32 allocates a Variable Length Array (VLA) on the stack whose size is derived from an attacker-controlled HTTP header field (Content-Type: multipart/form-data; boundary=...) without enforcing any length limit. Sending a boundary string longer than ~8000 characters overflows the 8192-byte task stack of the loopTask, causing a crash and potential remote code execution. This vulnerability is fixed in 3.3.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42854.json
- https://github.com/espressif/arduino-esp32/security/advisories/GHSA-8cmm-3887-r32j
- https://nvd.nist.gov/vuln/detail/CVE-2026-42854
