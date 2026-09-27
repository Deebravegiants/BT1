# [H] Bluetooth: classic: avdtp: missing buffer length check

## Summary
Severity: High
Advisory: CVE-2024-8798
Aliases: GHSA-r7pm-f93f-f7fp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-15
Source: https://osv.dev/vulnerability/CVE-2024-8798
Type: osv

## Details
No proper validation of the length of user input in olcp_ind_handler in zephyr/subsys/bluetooth/services/ots/ots_client.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8798.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-r7pm-f93f-f7fp
- https://nvd.nist.gov/vuln/detail/CVE-2024-8798
- https://github.com/zephyrproject-rtos/zephyr
