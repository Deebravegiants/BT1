# [C] ESF-IDF: Out-of-Bounds Write in ESP-TEE Secure Service Wrappers

## Summary
Severity: Critical
Advisory: CVE-2026-45328
Aliases: GHSA-mmgp-73p4-92xp
CVSS: 9.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45328
Type: osv

## Details
ESF-IDF is the Espressif Internet of Things (IOT) Development Framework. In versions 5.5.4 and 6.0, the esp_tee component exposes secure-service wrappers in esp_secure_services.c and esp_secure_services_iram.c that bridge calls from the user application (i.e. the REE) to TEE-protected hardware peripherals (AES, SHA, ECC, HMAC, SPI, MMU, WDT) and to the security feature like attestation, OTA updates, secure storage. This issue has been patched in versions 5.5.5 and 6.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45328.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-mmgp-73p4-92xp
- https://nvd.nist.gov/vuln/detail/CVE-2026-45328
- https://github.com/espressif/esp-idf/commit/145ba4c42dc8283054cfde9a1c3470db7399192f
- https://github.com/espressif/esp-idf/commit/440a5d1906502023f2a0fb0aecbdf0602d14acbf
- https://github.com/espressif/esp-idf/commit/764626a1b7c85b943d207da08a2f8f7d7f3def4d
- https://github.com/espressif/esp-idf/commit/7867f4a57560bf9fc4a931e37ba02b7a3e9f406b
- https://github.com/espressif/esp-idf/commit/afd14ab113acd0ca369965404c99ac42e74d4fcd
- https://github.com/espressif/esp-idf/commit/eebabaff2fdc273b1530fe66e55fb3bcd181dfd6
