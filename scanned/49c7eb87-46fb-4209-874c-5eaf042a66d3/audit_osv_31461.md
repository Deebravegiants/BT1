# [M] Bluetooth: Integer Overflow in Bluetooth Classic (BR/EDR) L2CAP

## Summary
Severity: Medium
Advisory: CVE-2025-12035
Aliases: GHSA-p793-3456-h7w3
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-12035
Type: osv

## Details
An integer overflow condition exists in Bluetooth Host stack, within the bt_br_acl_recv routine a critical path for processing inbound BR/EDR L2CAP traffic.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12035.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-p793-3456-h7w3
- https://nvd.nist.gov/vuln/detail/CVE-2025-12035
- https://github.com/zephyrproject-rtos/zephyr
