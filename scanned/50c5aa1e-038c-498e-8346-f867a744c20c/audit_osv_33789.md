# [C] Chamilo: Evaluation of untrusted user input leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2025-50187
Aliases: GHSA-356v-7xg2-3678
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-02
Source: https://osv.dev/vulnerability/CVE-2025-50187
Type: osv

## Details
Chamilo is a learning management system. Prior to version 1.11.28, parameter from SOAP request is evaluated without filtering which leads to Remote Code Execution. This issue has been patched in version 1.11.28.

## References
- https://github.com/chamilo/chamilo-lms/releases/tag/v1.11.28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50187.json
- https://github.com/chamilo/chamilo-lms/security/advisories/GHSA-356v-7xg2-3678
- https://nvd.nist.gov/vuln/detail/CVE-2025-50187
