# [M] ESF-IDF is Vulnerable to WPS Enrollee Fragment Integer Underflow

## Summary
Severity: Medium
Advisory: CVE-2026-25532
Aliases: GHSA-m2h2-683f-9mw7
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:H)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25532
Type: osv

## Details
ESF-IDF is the Espressif Internet of Things (IOT) Development Framework. In versions 5.5.2, 5.4.3, 5.3.4, 5.2.6, and 5.1.6, a vulnerability exists in the WPS (Wi-Fi Protected Setup) Enrollee implementation where malformed EAP-WSC packets with truncated payloads can cause integer underflow during fragment length calculation. When processing EAP-Expanded (WSC) messages, the code computes frag_len by subtracting header sizes from the total packet length. If an attacker sends a packet where the EAP Length field covers only the header and flags but omits the expected payload (such as the 2-byte Message Length field when WPS_MSG_FLAG_LEN is set), frag_len becomes negative. This negative value is then implicitly cast to size_t when passed to wpabuf_put_data(), resulting in a very large unsigned value. This issue has been patched in versions 5.5.3, 5.4.4, 5.3.5, 5.2.7, and 5.1.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25532.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-m2h2-683f-9mw7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25532
- https://github.com/espressif/esp-idf/commit/60f992a26de17bb5406f2149a2f8282dd7ad1c59
- https://github.com/espressif/esp-idf/commit/6f6766f917bc940ffbcc97eac4765a6ab15d5f79
- https://github.com/espressif/esp-idf/commit/73a587d42a57ece1962b6a4c530b574600650f63
- https://github.com/espressif/esp-idf/commit/b209fae993d795255827ce6b2b0d6942a377f5d4
- https://github.com/espressif/esp-idf/commit/b88befde6b5addcdd8d7373ce55c8052dea1e855
- https://github.com/espressif/esp-idf/commit/cad36beb4cde27abcf316cd90d8d8dddbc6f213a
- https://github.com/espressif/esp-idf/commit/de28801e8ea6a736b6f0db6fc0c682739363bb41
