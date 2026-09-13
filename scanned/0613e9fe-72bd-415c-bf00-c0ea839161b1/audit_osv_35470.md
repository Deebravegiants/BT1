# [H] Userspace privilege escalation vulnerability on Cortex M

## Summary
Severity: High
Advisory: CVE-2025-9408
Aliases: GHSA-3r6j-5mp3-75wr
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-11-11
Source: https://osv.dev/vulnerability/CVE-2025-9408
Type: osv

## Details
System call entry on Cortex M (and possibly R and A, but I think not) has a race which allows very practical privilege escalation for malicious userspace processes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/9xxx/CVE-2025-9408.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-3r6j-5mp3-75wr
- https://nvd.nist.gov/vuln/detail/CVE-2025-9408
- https://github.com/zephyrproject-rtos/zephyr
