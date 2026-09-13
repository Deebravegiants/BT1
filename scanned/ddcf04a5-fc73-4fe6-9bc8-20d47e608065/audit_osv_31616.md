# [H] Out of bounds read in dns_copy_qname

## Summary
Severity: High
Advisory: CVE-2025-1675
Aliases: GHSA-2m84-5hfw-m8v4
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2025-02-25
Source: https://osv.dev/vulnerability/CVE-2025-1675
Type: osv

## Details
The function dns_copy_qname in dns_pack.c performs performs a memcpy operation with an untrusted field and does not check if the source buffer is large enough to contain the copied data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1675.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-2m84-5hfw-m8v4
- https://nvd.nist.gov/vuln/detail/CVE-2025-1675
- https://github.com/zephyrproject-rtos/zephyr
