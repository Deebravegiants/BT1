# [M] ESPHome vulnerable to denial-of-service via out-of-bounds check bypass in the API component

## Summary
Severity: Medium
Advisory: GHSA-4h3h-63v6-88qx
CVE: CVE-2026-23833
CWE: CWE-190
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-21
Source: https://github.com/advisories/GHSA-4h3h-63v6-88qx
Type: github-advisory

## Affected
- PyPI: `esphome` — affected >=2025.9.0 <2025.12.7

## Details
### Summary
An integer overflow in the API component's protobuf decoder allows denial-of-service attacks when API encryption is not used.

### Details
The bounds check `ptr + field_length > end` in `components/api/proto.cpp` can overflow when a malicious client sends a large `field_length` value. This affects all ESPHome device platforms (ESP32, ESP8266, RP2040, LibreTiny). The overflow bypasses the out-of-bounds check, causing the device to read invalid memory and crash.

When using the plaintext API protocol, this attack can be performed without authentication. When noise encryption is enabled, knowledge of the encryption key is required.

### Affected Versions
ESPHome 2025.9.0 through 2025.12.6

### Mitigation
- Upgrade to ESPHome 2025.12.7 or later (or 2026.1.0b3 or later)
- [Enable API encryption](https://esphome.io/components/api.html#configuration-variables) with a unique key per device
- Follow the [Security Best Practices](https://esphome.io/guides/security_best_practices/)

### Severity
Low - Users following [Security Best Practices](https://esphome.io/guides/security_best_practices/) with API encryption enabled are not affected without knowledge of the encryption key.

### Impact
Denial-of-service. An attacker with network access to port 6053 can crash and reboot the device.

### Credits
Thanks to [@Mat931](https://github.com/Mat931) for responsibly reporting this vulnerability.

## References
- https://github.com/esphome/esphome/security/advisories/GHSA-4h3h-63v6-88qx
- https://nvd.nist.gov/vuln/detail/CVE-2026-23833
- https://github.com/esphome/esphome/pull/13306
- https://github.com/esphome/esphome/commit/69d7b6e9210390051318bd8e6410727689de08d6
- https://esphome.io/guides/security_best_practices
- https://github.com/esphome/esphome
