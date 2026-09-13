# [H] ESF-IDF: Stack-Based Out-of-Bounds Write in JPEG Decoder DQT Marker Parsing

## Summary
Severity: High
Advisory: CVE-2026-55687
Aliases: GHSA-v6r2-f6p2-88cj
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55687
Type: osv

## Details
ESF-IDF is the Espressif Internet of Things (IOT) Development Framework. Versions 6.0.1, 5.5.4, 5.4.4, 5.3.5, and possibly prior contain an out-of-bounds write in jpeg_parse_dqt_marker() in components/esp_driver_jpeg/jpeg_parse_marker.c because the attacker-controlled DQT marker Tq nibble is used as an index into the qt_tbl array without validating that it is in the range 0..3, allowing malformed JPEG input to corrupt stack memory and reliably trigger a denial of service. This issue is fixed in version 6.0.2 and is expected to be fixed in versions 5.5.5, 5.4.5, and 5.3.6.

## References
- https://github.com/espressif/esp-idf/releases/tag/v6.0.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55687.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-v6r2-f6p2-88cj
- https://nvd.nist.gov/vuln/detail/CVE-2026-55687
- https://github.com/espressif/esp-idf/commit/303c01305acb8ae5c4eb24a1786300681b4822a4
- https://github.com/espressif/esp-idf/commit/6ffafe8e93142ef8ffe51a6311d4abfc0f10fe77
- https://github.com/espressif/esp-idf/commit/7ccfc00f39faf1b7e5919f45b56fe44ba699d7c1
- https://github.com/espressif/esp-idf/commit/82c5c2dad45313786fb7e973059bc9094d95c3b2
- https://github.com/espressif/esp-idf/commit/f2df45bcedef11354e83c31a9718d680a68422c4
