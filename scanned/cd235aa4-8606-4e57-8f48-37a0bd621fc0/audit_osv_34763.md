# [M] MaxKB has Information Leak in sandbox

## Summary
Severity: Medium
Advisory: CVE-2025-64703
Aliases: GHSA-qwvm-x4xh-g2qq
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-11-13
Source: https://osv.dev/vulnerability/CVE-2025-64703
Type: osv

## Details
MaxKB is an open-source AI assistant for enterprise. In versions prior to 2.3.1, a user can get sensitive informations by Python code in tool module, although the process run in sandbox. Version 2.3.1 fixes the issue.

## References
- https://github.com/1Panel-dev/MaxKB/security/advisories/GHSA-qwvm-x4xh-g2qq
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64703.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-64703
