# [H] Directus: Path Traversal and Broken Access Control in File Management API

## Summary
Severity: High
Advisory: GHSA-393c-p46r-7c95
CVE: CVE-2026-39942
CWE: CWE-284, CWE-639, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-393c-p46r-7c95
Type: github-advisory

## Affected
- npm: `directus` — affected >=0 <11.17.0

## Details
## Summary

A broken access control vulnerability was identified in the Directus file management API that allows authenticated users to overwrite files belonging to other users by manipulating the `filename_disk` parameter.

## Details

The `PATCH /files/{id}` endpoint accepts a user-controlled `filename_disk` parameter. By setting this value to match the storage path of another user's file, an attacker can overwrite that file's content while manipulating metadata fields such as `uploaded_by` to obscure the tampering.

## Impact

- **Unauthorized File Overwrite**: Attackers can replace legitimate files with malicious content, creating significant risk of malware propagation and data corruption.
- **Remote Code Execution**: If the storage backend is shared with the extensions location, attackers can deploy malicious extensions that execute arbitrary code when loaded.
- **Data Integrity Compromise**: Files can be tampered with or replaced without visible indication in the application interface.

## Mitigation

The `filename_disk` parameter should be treated as a server-controlled value. Uniqueness of storage paths must be enforced server-side, and `filename_disk` should be excluded from the fields users are permitted to update directly.

## References
- https://github.com/directus/directus/security/advisories/GHSA-393c-p46r-7c95
- https://nvd.nist.gov/vuln/detail/CVE-2026-39942
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v11.17.0
