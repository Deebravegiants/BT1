# [C] ESP-NOW Integer Underflow Vulnerability Advisory

## Summary
Severity: Critical
Advisory: CVE-2025-52471
Aliases: GHSA-hqhh-cp47-fv5g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-06-24
Source: https://osv.dev/vulnerability/CVE-2025-52471
Type: osv

## Details
ESF-IDF is the Espressif Internet of Things (IOT) Development Framework. An integer underflow vulnerability has been identified in the ESP-NOW protocol implementation within the ESP Wi-Fi component of versions 5.4.1, 5.3.3, 5.2.5, and 5.1.6 of the ESP-IDF framework. This issue stems from insufficient validation of user-supplied data length in the packet receive function. Under certain conditions, this may lead to out-of-bounds memory access and may allow arbitrary memory write operations. On systems without a memory protection scheme, this behavior could potentially be used to achieve remote code execution (RCE) on the target device. In versions 5.4.2, 5.3.4, 5.2.6, and 5.1.6, ESP-NOW has added more comprehensive validation logic on user-supplied data length during packet reception to prevent integer underflow caused by negative value calculations. For ESP-IDF v5.3 and earlier, a workaround can be applied by validating that the `data_len` parameter received in the RX callback (registered via `esp_now_register_recv_cb()`) is a positive value before further processing. For ESP-IDF v5.4 and later, no application-level workaround is available. Users are advised to upgrade to a patched version of ESP-IDF to take advantage of the built-in mitigation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52471.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-hqhh-cp47-fv5g
- https://nvd.nist.gov/vuln/detail/CVE-2025-52471
- https://github.com/espressif/esp-idf/commit/b1a379d57430d265a53aca13d59ddfbf2e7ac409
- https://github.com/espressif/esp-idf/commit/c5fc81917805f99e687c81cc56b68dc5df7ef8b5
- https://github.com/espressif/esp-idf/commit/d4dafbdc3572387cd4f9a62b776580bc4ac3bde7
- https://github.com/espressif/esp-idf/commit/d6ec5a52255b17c1d6ef379e89f9de2c379042f8
- https://github.com/espressif/esp-idf/commit/df7757d8279871fa7a2f42ef3962c6c1ec88b8a2
- https://github.com/espressif/esp-idf/commit/edc227c5eaeced999b5212943a9434379f8aad80
