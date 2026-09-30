# [H] OpenEMR has IDOR in Patient Notes Web UI allows unauthorized note access/modification

## Summary
Severity: High
Advisory: CVE-2026-34055
Aliases: GHSA-8gj5-r8vm-mghq
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-34055
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, the legacy patient notes functions in `library/pnotes.inc.php` perform updates and deletes using `WHERE id = ?` without verifying that the note belongs to a patient the user is authorized to access. Multiple web UI callers pass user-controlled note IDs directly to these functions. This is the same class of vulnerability as CVE-2026-25745 (REST API IDOR), but affects the web UI code paths. Version 8.0.0.3 patches the issue.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34055.json
- https://github.com/openemr/openemr/security/advisories/GHSA-8gj5-r8vm-mghq
- https://nvd.nist.gov/vuln/detail/CVE-2026-34055
- https://github.com/openemr/openemr/commit/214c9b4585a6f1c8c22750172d47f0e258fec0bf
