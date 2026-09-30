# [H] OpenEMR Missing Authorization in Procedure Order AJAX Deletion Handler

## Summary
Severity: High
Advisory: CVE-2026-34053
Aliases: GHSA-3vvq-pfq6-pw98
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-34053
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, missing authorization in the AJAX deletion endpoint `interface/forms/procedure_order/handle_deletions.php` allows any authenticated user, regardless of role, to irreversibly delete procedure orders, answers, and specimens belonging to any patient in the system. Version 8.0.0.3 patches the issue.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34053.json
- https://github.com/openemr/openemr/security/advisories/GHSA-3vvq-pfq6-pw98
- https://nvd.nist.gov/vuln/detail/CVE-2026-34053
- https://github.com/openemr/openemr/commit/7a16b731af7d34ffd92155fe2a5692fa1a67858e
