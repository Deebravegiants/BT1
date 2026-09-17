# [H] bt: hci: DoS and possible RCE

## Summary
Severity: High
Advisory: CVE-2023-4424
Aliases: GHSA-j4qm-xgpf-qjw3
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:H)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-4424
Type: osv

## Details
An malicious BLE device can cause buffer overflow by sending malformed advertising packet BLE device using Zephyr OS, leading to DoS or potential RCE on the victim BLE device.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/4xxx/CVE-2023-4424.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-j4qm-xgpf-qjw3
- https://nvd.nist.gov/vuln/detail/CVE-2023-4424
- https://github.com/zephyrproject-rtos/zephyr
