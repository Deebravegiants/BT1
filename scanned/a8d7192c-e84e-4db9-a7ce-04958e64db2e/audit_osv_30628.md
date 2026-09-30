# [H] CVE-2024-53406

## Summary
Severity: High
Advisory: CVE-2024-53406
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-03-13
Source: https://osv.dev/vulnerability/CVE-2024-53406
Type: osv

## Details
Espressif Esp idf v5.3.0 is vulnerable to Insecure Permissions resulting in Authentication bypass. In the reconnection phase, the device reuses the session key from a previous connection session, creating an opportunity for attackers to execute security bypass attacks.

## References
- https://github.com/yangting111/BLE_TEST/blob/main/result/PoC/Esp/sk_reuse.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53406.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53406
- https://github.com/espressif/esp-idf
