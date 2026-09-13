# [H] Bluetooth: bt_conn_tx_processor unsafe handling

## Summary
Severity: High
Advisory: CVE-2025-7403
Aliases: GHSA-9r46-cqqw-6j2j
CVSS: 7.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-7403
Type: osv

## Details
Unsafe handling in bt_conn_tx_processor causes a use-after-free, resulting in a write-before-zero. The written 4 bytes are attacker-controlled, enabling precise memory corruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7403.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-9r46-cqqw-6j2j
- https://nvd.nist.gov/vuln/detail/CVE-2025-7403
- https://github.com/zephyrproject-rtos/zephyr
