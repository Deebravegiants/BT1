# [H] Bluetooth: Semi-Arbitrary ability to make the BLE Target send disconnection requests

## Summary
Severity: High
Advisory: CVE-2025-10456
Aliases: GHSA-hcc8-3qr7-c9m8
CVSS: 7.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-10456
Type: osv

## Details
A vulnerability was identified in the handling of Bluetooth Low Energy (BLE) fixed channels (such as SMP or ATT). Specifically, an attacker could exploit a flaw that causes the BLE target (i.e., the device under attack) to attempt to disconnect a fixed channel, which is not allowed per the Bluetooth specification. This leads to undefined behavior, including potential assertion failures, crashes, or memory corruption, depending on the BLE stack implementation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10456.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-hcc8-3qr7-c9m8
- https://nvd.nist.gov/vuln/detail/CVE-2025-10456
- https://github.com/zephyrproject-rtos/zephyr
