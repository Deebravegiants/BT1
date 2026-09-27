# [M] ESF-IDF Has Out-of-Bounds Write in ESP32 Bluetooth AVRCP Vendor Command Handling

## Summary
Severity: Medium
Advisory: CVE-2025-68474
Aliases: GHSA-43gh-7r4f-qp57
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:H/SC:L/SI:L/SA:L)
Published: 2025-12-26
Source: https://osv.dev/vulnerability/CVE-2025-68474
Type: osv

## Details
ESF-IDF is the Espressif Internet of Things (IOT) Development Framework. In versions 5.5.1, 5.4.3, 5.3.4, 5.2.6, 5.1.6, and earlier, in the avrc_vendor_msg() function of the ESP-IDF BlueDroid AVRCP stack, the allocated buffer size was validated using AVRC_MIN_CMD_LEN (20 bytes). However, the actual fixed header data written before the vendor payload exceeds this value. This totals 29 bytes written before p_msg->p_vendor_data is copied. Using the old AVRC_MIN_CMD_LEN could allow an out-of-bounds write if vendor_len approaches the buffer limit. For commands where vendor_len is large, the original buffer allocation may be insufficient, causing writes beyond the allocated memory. This can lead to memory corruption, crashes, or other undefined behavior. The overflow could be larger when assertions are disabled.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68474.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-43gh-7r4f-qp57
- https://nvd.nist.gov/vuln/detail/CVE-2025-68474
- https://github.com/espressif/esp-idf/commit/0b0b59f2e19cb99dfa1b28c284d1c5c1d276a132
- https://github.com/espressif/esp-idf/commit/565fa98d0cfd58102204c1cb636747e17ee59845
- https://github.com/espressif/esp-idf/commit/8262ee807d5cd425f66304f703eeb3382fb888c0
- https://github.com/espressif/esp-idf/commit/a6c1bc5e3e91ad1cb964ce2c178ee40a5d10a4a0
- https://github.com/espressif/esp-idf/commit/aa0e3d75db995b7137b55349fc92ee684b47092d
- https://github.com/espressif/esp-idf/commit/b9ba1e29b65536ab4b670ac099585d09adce0376
