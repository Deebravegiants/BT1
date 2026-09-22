# [M] ESF-IDF: Heap Out-of-Bounds Read in Bluedroid AVRCP Target Parser

## Summary
Severity: Medium
Advisory: CVE-2026-46532
Aliases: GHSA-3pp8-42fh-3j3c
CVSS: 4.6 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-46532
Type: osv

## Details
ESF-IDF is the Espressif Internet of Things (IOT) Development Framework. In versions 5.2.6, 5.3.5, 5.4.4, 5.5.3, and 6.0, an out-of-bounds read exists in the BlueDroid AVRCP vendor-command parser (avrc_pars_vendor_cmd() in components/bt/host/bluedroid/stack/avrc/avrc_pars_tg.c). This issue has been patched in versions 5.2.7, 5.3.6, 5.4.5, 5.5.4, and 6.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46532.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-3pp8-42fh-3j3c
- https://nvd.nist.gov/vuln/detail/CVE-2026-46532
- https://github.com/espressif/esp-idf/commit/56053c4d1f37955ccf296cf2f6dfd0f7ebd4fae6
- https://github.com/espressif/esp-idf/commit/60f9362f83a05942069532f357c234cd5e5d4302
- https://github.com/espressif/esp-idf/commit/7c004d3fe3022f5f0db98dd1b2d0648a3a9cfb3f
- https://github.com/espressif/esp-idf/commit/8746e5f7e762ead84d2902edec34d84cdd701b2b
- https://github.com/espressif/esp-idf/commit/b0959b5ab1dc60398a916c80f14b1816780c801e
- https://github.com/espressif/esp-idf/commit/c53d05ae526607ca5eae9ffedaf57775eec33a4f
