# [M] OpenEMR has Broken Access Control that allows unauthorized access to EDI Logs

## Summary
Severity: Medium
Advisory: CVE-2026-24896
Aliases: GHSA-rccq-vjfg-ggjh
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-24896
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0, a Broken Access Control vulnerability exists in OpenEMR’s edih_main.php endpoint, which allows any authenticated user—including low-privilege roles like Receptionist—to access EDI log files by manipulating the log_select parameter in a GET request. The back-end fails to enforce role-based access control (RBAC), allowing sensitive system logs to be accessed outside the GUI-enforced permission boundaries. Version 8.0.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24896.json
- https://github.com/openemr/openemr/security/advisories/GHSA-rccq-vjfg-ggjh
- https://nvd.nist.gov/vuln/detail/CVE-2026-24896
- https://github.com/openemr/openemr/commit/1a57dfc244b30e96e7ebdb5ba6f331a6eb868df1
