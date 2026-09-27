# [H] Improper validation of NBNS name_len in arduino-esp32 NetBIOS leads to memory corruption

## Summary
Severity: High
Advisory: CVE-2026-41429
Aliases: GHSA-92j9-c75g-2c5f
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41429
Type: osv

## Details
arduino-esp32 is an Arduino core for the ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6 and ESP32-H2 microcontrollers. Prior to 3.3.8, there is a remotely reachable memory corruption issue in the NBNS packet handling path. When NetBIOS is enabled by calling NBNS.begin(...), the device listens on UDP port 137 and processes untrusted NBNS requests from the local network.
The request parser trusts the attacker-controlled name_len field without enforcing a bound consistent with the fixed-size destination buffers used later in the flow. This vulnerability is fixed in 3.3.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41429.json
- https://github.com/espressif/arduino-esp32/security/advisories/GHSA-92j9-c75g-2c5f
- https://nvd.nist.gov/vuln/detail/CVE-2026-41429
