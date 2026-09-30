# [H] Chamilo: Error-based SQL Injection via GET openid.assoc_handle with the /index.php script

## Summary
Severity: High
Advisory: CVE-2025-50190
Aliases: GHSA-5296-jxrr-pfwj
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2025-50190
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.30, there is an error-based SQL Injection via the GET openid.assoc_handle parameter with the /index.php script. This issue has been patched in version 1.11.30.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50190.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-5296-jxrr-pfwj
- https://nvd.nist.gov/vuln/detail/CVE-2025-50190
- https://github.com/chamilo/chamilo-lms/commit/613eb19a0fac6dd49c233f32ad5428cd29d5a468
