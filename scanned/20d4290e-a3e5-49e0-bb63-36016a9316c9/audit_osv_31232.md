# [M] Bluetooth: ots: missing buffer length check

## Summary
Severity: Medium
Advisory: CVE-2024-6444
Aliases: GHSA-qj4r-chj6-h7qp
CVSS: 6.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-10-04
Source: https://osv.dev/vulnerability/CVE-2024-6444
Type: osv

## Details
No proper validation of the length of user input in olcp_ind_handler in zephyr/subsys/bluetooth/services/ots/ots_client.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6444.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-qj4r-chj6-h7qp
- https://nvd.nist.gov/vuln/detail/CVE-2024-6444
- https://github.com/zephyrproject-rtos/zephyr
