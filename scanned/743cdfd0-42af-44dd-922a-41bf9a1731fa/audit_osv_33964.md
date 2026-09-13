# [M] ESPAsyncWebServer Vulnerable to CRLF Injection in AsyncWebHeader.cpp

## Summary
Severity: Medium
Advisory: CVE-2025-53094
Aliases: GHSA-87j8-6f7g-h8wh
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-06-27
Source: https://osv.dev/vulnerability/CVE-2025-53094
Type: osv

## Details
ESPAsyncWebServer is an asynchronous HTTP and WebSocket server library for ESP32, ESP8266, RP2040 and RP2350. In versions up to and including 3.7.8, a CRLF (Carriage Return Line Feed) injection vulnerability exists in the construction and output of HTTP headers within `AsyncWebHeader.cpp`. Unsanitized input allows attackers to inject CR (`\r`) or LF (`\n`) characters into header names or values, leading to arbitrary header or response manipulation. Manipulation of HTTP headers and responses can enable a wide range of attacks, making the severity of this vulnerability high. A fix is available at pull request 211 and is expected to be part of version 3.7.9.

## References
- https://github.com/ESP32Async/ESPAsyncWebServer/blob/1095dfd1ecf1a903aede29854232af1b24f089b1/src/AsyncWebHeader.cpp#L6-L32
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53094.json
- https://github.com/ESP32Async/ESPAsyncWebServer/security/advisories/GHSA-87j8-6f7g-h8wh
- https://nvd.nist.gov/vuln/detail/CVE-2025-53094
- https://github.com/ESP32Async/ESPAsyncWebServer/pull/211
