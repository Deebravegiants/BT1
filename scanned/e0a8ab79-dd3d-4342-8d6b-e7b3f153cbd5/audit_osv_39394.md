# [H] ESF-IDF: Heap buffer overflow in protocomm Security2 over Bluetooth

## Summary
Severity: High
Advisory: CVE-2026-45542
Aliases: GHSA-9r76-858f-v6jh
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45542
Type: osv

## Details
ESF-IDF is the Espressif Internet of Things (IOT) Development Framework. In versions 5.2.6, 5.3.5, 5.4.4, 5.5.4, and 6.0, a heap buffer overflow exists in the Security Scheme 2 (SRP6a) session-setup path of the protocomm component. The first-phase handler (handle_session_command0() in components/protocomm/src/security/security2.c) trusts the length of a client-supplied protobuf field for the SRP6a username and copies it into a buffer whose size is derived from a narrower destination type. The resulting truncation-versus-copy asymmetry corrupts the heap when an oversized value is supplied. This issue has been patched in versions 5.2.7, 5.3.6, 5.4.5, 5.5.5, and 6.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45542.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-9r76-858f-v6jh
- https://nvd.nist.gov/vuln/detail/CVE-2026-45542
- https://github.com/espressif/esp-idf/commit/0ea58d79845ad674d0358d5de246015a68c4cb4f
- https://github.com/espressif/esp-idf/commit/56c3e385611e63162d0f2f8504ac4ae2ccfccef0
- https://github.com/espressif/esp-idf/commit/71eb2dbe6aaef830719ecac8edf409e2992b64b2
- https://github.com/espressif/esp-idf/commit/9b4cacf9cbc69379972de6a2247fcf5af9240961
- https://github.com/espressif/esp-idf/commit/a2f4554f10ba075c98cbc67464db096ba32497cf
- https://github.com/espressif/esp-idf/commit/f5d24a7e919bc5f447091479656b86da6762a103
