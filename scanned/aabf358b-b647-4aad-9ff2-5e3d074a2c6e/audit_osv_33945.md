# [C] arduino-esp32 vulnerable to CRLF injection in WebServer.cpp

## Summary
Severity: Critical
Advisory: CVE-2025-53007
Aliases: GHSA-5476-9jjq-563m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-06-26
Source: https://osv.dev/vulnerability/CVE-2025-53007
Type: osv

## Details
arduino-esp32 provides an Arduino core for the ESP32. Versions prior to 3.3.0-RC1 and 3.2.1 contain a HTTP Response Splitting vulnerability. The `sendHeader` function takes arbitrary input for the HTTP header name and value, concatenates them into an HTTP header line, and appends this to the outgoing HTTP response headers. There is no validation or sanitization of the `name` or `value` parameters before they are included in the HTTP response. If an attacker can control the input to `sendHeader` (either directly or indirectly), they could inject carriage return (`\r`) or line feed (`\n`) characters into either the header name or value. This could allow the attacker to inject additional headers, manipulate the structure of the HTTP response, potentially inject an entire new HTTP response (HTTP Response Splitting), and/or ause header confusion or other HTTP protocol attacks. Versions 3.3.0-RC1 and 3.2.1 contain a fix for the issue.

## References
- https://github.com/espressif/arduino-esp32/blob/9e61fa7e4bce59c05cb17c15b11b53b9bafca077/libraries/WebServer/src/WebServer.cpp#L504-L521
- https://github.com/espressif/arduino-esp32/blob/9e61fa7e4bce59c05cb17c15b11b53b9bafca077/libraries/WebServer/src/WebServer.cpp#L577-L582
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53007.json
- https://github.com/espressif/arduino-esp32/security/advisories/GHSA-5476-9jjq-563m
- https://nvd.nist.gov/vuln/detail/CVE-2025-53007
- https://github.com/espressif/arduino-esp32/commit/21640ac82a1bb5efa8cf0b3841be1ac80add6785
