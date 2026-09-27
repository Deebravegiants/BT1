# [M] NavigaTUM has a Path Traversal Vulnerability in the propose_edits functionality

## Summary
Severity: Medium
Advisory: CVE-2026-25575
Aliases: GHSA-59hj-f48w-hjfm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25575
Type: osv

## Details
NavigaTUM is a website and API to search for rooms, buildings and other places. Prior to commit 86f34c7, there is a path traversal vulnerability in the propose_edits endpoint allows unauthenticated users to overwrite files in directories writable by the application user (e.g., /cdn). By supplying unsanitized file keys containing traversal sequences (e.g., ../../) in the JSON payload, an attacker can escape the intended temporary directory and replace public facing images or fill the server's storage. This issue has been patched via commit 86f34c7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25575.json
- https://github.com/TUM-Dev/NavigaTUM/security/advisories/GHSA-59hj-f48w-hjfm
- https://nvd.nist.gov/vuln/detail/CVE-2026-25575
- https://github.com/TUM-Dev/NavigaTUM/commit/86f34c72886a59ec8f1e6c00f78a5ab889a70fd0
- https://github.com/TUM-Dev/NavigaTUM/pull/2650
