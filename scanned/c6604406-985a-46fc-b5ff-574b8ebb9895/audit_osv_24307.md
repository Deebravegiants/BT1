# [C] DoS: Invalid Initialization in le_read_buffer_size_complete

## Summary
Severity: Critical
Advisory: CVE-2023-0397
Aliases: GHSA-wc2h-h868-q7hj
CVSS: 9.6 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:L/I:H/A:H)
Published: 2023-01-19
Source: https://osv.dev/vulnerability/CVE-2023-0397
Type: osv

## Details
A malicious / defect bluetooth controller can cause a Denial of Service due to unchecked input in le_read_buffer_size_complete.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0397.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-wc2h-h868-q7hj
- https://nvd.nist.gov/vuln/detail/CVE-2023-0397
