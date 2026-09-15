# [M] Anti Rollback bypass with physical access and TOCTOU attack

## Summary
Severity: Medium
Advisory: CVE-2024-28183
Aliases: GHSA-22x6-3756-pfp8
CVSS: 6.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2024-28183
Type: osv

## Details
ESP-IDF is the development framework for Espressif SoCs supported on Windows, Linux and macOS. A Time-of-Check to Time-of-Use (TOCTOU) vulnerability was discovered in the implementation of the ESP-IDF bootloader which could allow an attacker with physical access to flash of the device to bypass anti-rollback protection. Anti-rollback prevents rollback to application with security version lower than one programmed in eFuse of chip. This attack can allow to boot past (passive) application partition having lower security version of the same device even in the presence of the flash encryption scheme. The attack requires carefully modifying the flash contents after the anti-rollback checks have been performed by the bootloader (before loading the application). The vulnerability is fixed in 4.4.7 and 5.2.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28183.json
- https://github.com/espressif/esp-idf/security/advisories/GHSA-22x6-3756-pfp8
- https://nvd.nist.gov/vuln/detail/CVE-2024-28183
- https://github.com/espressif/esp-idf/commit/3305cb4d235182067936f8e940e6db174e25b4b2
- https://github.com/espressif/esp-idf/commit/4c95aa445d4e84f01f86b6f3a552aa299276abf3
- https://github.com/espressif/esp-idf/commit/534e3ad1fa68526a5f989fb2163856d6b7cd2c87
- https://github.com/espressif/esp-idf/commit/7003f1ef0dffc73c34eb153d1b0710babb078149
- https://github.com/espressif/esp-idf/commit/b2cdc0678965790f49afeb6e6b0737cd24433a05
- https://github.com/espressif/esp-idf/commit/c33b9e1426121ce8cccf1a94241740be9cff68de
- https://github.com/espressif/esp-idf/commit/f327ddf6adab0c28d395975785727b2feef57803
