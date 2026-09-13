# [M] Bluetooth: peripheral: Invalid handling of malformed connection request

## Summary
Severity: Medium
Advisory: CVE-2025-12890
Aliases: GHSA-8hrf-pfww-83v9
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-11-07
Source: https://osv.dev/vulnerability/CVE-2025-12890
Type: osv

## Details
Improper handling of  malformed Connection Request with the interval set to be 1 (which supposed to be illegal) and the chM 0x7CFFFFFFFF triggers a crash. The peripheral will not be connectable after it.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/12xxx/CVE-2025-12890.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-8hrf-pfww-83v9
- https://nvd.nist.gov/vuln/detail/CVE-2025-12890
- https://github.com/zephyrproject-rtos/zephyr
