# [M] CFiles Unauthorized Folder/ZIP Access in Public Spaces

## Summary
Severity: Medium
Advisory: CVE-2025-65963
Aliases: GHSA-rv2x-7qwp-2hf4
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/CVE-2025-65963
Type: osv

## Details
Files is a module for managing files inside spaces and user profiles. Prior to versions 0.16.11 and 0.17.2, insufficient authorization checks allow non-member users to create new folders, up- and download files as a ZIP archive in public spaces. Private spaces are not affected. This issue has been patched in versions 0.16.11 and 0.17.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65963.json
- https://github.com/humhub/cfiles/security/advisories/GHSA-rv2x-7qwp-2hf4
- https://nvd.nist.gov/vuln/detail/CVE-2025-65963
- https://github.com/humhub/cfiles/commit/75698f8e8f360cea470f0e9f264015b697ab4c09
