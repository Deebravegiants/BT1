# [H] arduino-esp32: Digest authentication URI mismatch bypass in WebServer allows cross-resource replay attack

## Summary
Severity: High
Advisory: CVE-2026-42855
Aliases: GHSA-28hv-fwm3-rpcq
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-42855
Type: osv

## Details
arduino-esp32 is an Arduino core for the ESP32, ESP32-S2, ESP32-S3, ESP32-C3, ESP32-C6 and ESP32-H2 microcontrollers. Prior to 3.3.8, the WebServer Digest authentication implementation in arduino-esp32 computes the authentication hash using the URI field from the client's Authorization header, without verifying that it matches the actual requested URI. This allows an attacker who possesses any valid digest response (computed for URI-A) to authenticate requests to a completely different protected URI (URI-B), bypassing per-resource access control. This vulnerability is fixed in 3.3.8.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42855.json
- https://github.com/espressif/arduino-esp32/security/advisories/GHSA-28hv-fwm3-rpcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42855
