# [M] Bluetooth: Out-Of-Context le_conn_rsp Handling

## Summary
Severity: Medium
Advisory: CVE-2025-10457
Aliases: GHSA-xqj6-vh76-2vv8
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-09-19
Source: https://osv.dev/vulnerability/CVE-2025-10457
Type: osv

## Details
The function responsible for handling BLE connection responses does not verify whether a response is expected—that is, whether the device has initiated a connection request. Instead, it relies solely on identifier matching.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/10xxx/CVE-2025-10457.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-xqj6-vh76-2vv8
- https://nvd.nist.gov/vuln/detail/CVE-2025-10457
- https://github.com/zephyrproject-rtos/zephyr
