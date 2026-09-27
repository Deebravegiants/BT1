# [H] Out of bounds read when calling crc16_ansi and strlen in dns_validate_msg

## Summary
Severity: High
Advisory: CVE-2025-1673
Aliases: GHSA-jjhx-rrh4-j8mx
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2025-02-25
Source: https://osv.dev/vulnerability/CVE-2025-1673
Type: osv

## Details
A malicious or malformed DNS packet without a payload can cause an out-of-bounds read, resulting in a crash (denial of service) or an incorrect computation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/1xxx/CVE-2025-1673.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-jjhx-rrh4-j8mx
- https://nvd.nist.gov/vuln/detail/CVE-2025-1673
- https://github.com/zephyrproject-rtos/zephyr
