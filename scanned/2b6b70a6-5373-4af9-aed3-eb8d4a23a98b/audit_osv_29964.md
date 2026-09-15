# [M] Chamilo: Post-Auth Remote Code Execution

## Summary
Severity: Medium
Advisory: CVE-2024-47886
Aliases: GHSA-c4fc-vjm9-9mvc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2024-47886
Type: osv

## Details
Chamilo is a learning management system. Chamillo is affected by a post-authentication phar unserialize which leads to a remote code execution (RCE) within versions 1.11.12 to 1.11.26. By abusing multiple supported features from the virtualization plugin vchamilo, the vulnerability allows an administrator to execute arbitrary code on the server. This issue has been patched in version 1.11.26.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47886.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-c4fc-vjm9-9mvc
- https://nvd.nist.gov/vuln/detail/CVE-2024-47886
