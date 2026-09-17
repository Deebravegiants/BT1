# [M] ESF-IDF: Out-of-bounds Read in lwIP DHCP Server Option Parser

## Summary
Severity: Medium
Advisory: CVE-2026-45160
Aliases: GHSA-g764-gwc3-75m5
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-10
Source: https://osv.dev/vulnerability/CVE-2026-45160
Type: osv

## Details
ESF-IDF is the Espressif Internet of Things (IOT) Development Framework. In versions 5.2.7, 5.3.5, 5.4.4, 5.5.4, and 6.0.1, an out-of-bounds read flaw exists in the DHCP server option parser (parse_options() in components/lwip/apps/dhcpserver/dhcpserver.c) shipped with ESP-IDF's lwIP component. The parser walks the BOOTP/DHCP options field without validating that each option's length byte and declared payload length stay within the received packet buffer. A crafted DHCP request can cause the parser to read past the end of the options buffer into adjacent heap memory. The issue affects the DHCP server used by ESP-IDF's SoftAP and any configuration where the device runs as a DHCP server on a local network. This issue has been patched in versions 5.2.8, 5.3.6, 5.4.5, 5.5.5, and 6.0.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45160.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-g764-gwc3-75m5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45160
- https://github.com/espressif/esp-idf/commit/2bf4dd12002dbae60a4b21abff010ecb2b8ee82b
- https://github.com/espressif/esp-idf/commit/2da2db43fd7e0bcff9e7b95f54f388296bb6f911
- https://github.com/espressif/esp-idf/commit/8b4b5d5301815198d177974ffc24848f47748248
- https://github.com/espressif/esp-idf/commit/9f713dbc94982d917f2d12964b233cd9efa4aeba
- https://github.com/espressif/esp-idf/commit/d51b1076092487e533eadf8b48c9c8579d3a6712
- https://github.com/espressif/esp-idf/commit/fba5f995436a3e3139f768b6d8f1a74d5ce1d318
