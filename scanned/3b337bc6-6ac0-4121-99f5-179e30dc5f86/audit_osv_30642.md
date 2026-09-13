# [M] AES/CBC Constant IV Vulnerability in ESPTouch v2

## Summary
Severity: Medium
Advisory: CVE-2024-53845
Aliases: GHSA-wm57-466g-mhrr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2024-12-11
Source: https://osv.dev/vulnerability/CVE-2024-53845
Type: osv

## Details
ESPTouch is a connection protocol for internet of things devices. In the ESPTouchV2 protocol, while there is an option to use a custom AES key, there is no option to set the IV (Initialization Vector) prior to versions 5.3.2, 5.2.4, 5.1.6, and 5.0.8. The IV is set to zero and remains constant throughout the product's lifetime. In AES/CBC mode, if the IV is not properly initialized, the encrypted output becomes deterministic, leading to potential data leakage. To address the aforementioned issues, the application generates a random IV when activating the AES key starting in versions 5.3.2, 5.2.4, 5.1.6, and 5.0.8. This IV is then transmitted along with the provision data to the provision device. The provision device has also been equipped with a parser for the AES IV. The upgrade is applicable for all applications and users of ESPTouch v2 component from ESP-IDF. As it is implemented in the ESP Wi-Fi stack, there is no workaround for the user to fix the application layer without upgrading the underlying firmware.

## References
- https://github.com/EspressifApp/EsptouchForAndroid/tree/master/esptouch-v2
- https://github.com/EspressifApp/EsptouchForIOS/tree/master/EspTouchDemo/ESPTouchV2
- https://github.com/espressif/esp-idf/tree/master/components/esp_wifi
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53845.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-wm57-466g-mhrr
- https://nvd.nist.gov/vuln/detail/CVE-2024-53845
- https://github.com/espressif/esp-idf/commit/4f85a2726e04b737c8646d865b44ddd837b703db
- https://github.com/espressif/esp-idf/commit/8fb28dcedcc49916a5206456a3a61022d4302cd8
- https://github.com/espressif/esp-idf/commit/d47ed7d6f814e21c5bc8997ab0bc68e2360e5cb2
- https://github.com/espressif/esp-idf/commit/de69895f38d563e22228f5ba23fffa02feabc3a9
- https://github.com/espressif/esp-idf/commit/fd224e83bbf133833638b277c767be7f7cdd97c7
