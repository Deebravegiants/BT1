# [M] HCI send_sync Dangling Semaphore Reference Re-use

## Summary
Severity: Medium
Advisory: CVE-2023-1901
Aliases: GHSA-xvvm-8mcm-9cq3
CVSS: 5.9 (CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-07-10
Source: https://osv.dev/vulnerability/CVE-2023-1901
Type: osv

## Details
The bluetooth HCI host layer logic not clearing a global reference to a semaphore after synchronously sending HCI commands may allow a malicious HCI Controller to cause the use of a dangling reference in the host layer, leading to a crash (DoS) or potential RCE on the Host layer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/1xxx/CVE-2023-1901.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-xvvm-8mcm-9cq3
- https://nvd.nist.gov/vuln/detail/CVE-2023-1901
- https://github.com/zephyrproject-rtos/zephyr
