# [H] Missing Security Control in Zephyr OS IP Packet Handling

## Summary
Severity: High
Advisory: CVE-2023-7060
Aliases: GHSA-fjc8-223c-qgqr
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2023-7060
Type: osv

## Details
Zephyr OS IP packet handling does not properly drop IP packets arriving on an external interface with a source address equal to 127.0.01 or the destination address.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/7xxx/CVE-2023-7060.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-fjc8-223c-qgqr
- https://nvd.nist.gov/vuln/detail/CVE-2023-7060
- https://github.com/zephyrproject-rtos/zephyr
