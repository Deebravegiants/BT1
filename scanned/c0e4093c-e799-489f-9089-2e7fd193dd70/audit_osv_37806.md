# [H] FileRise ONLYOFFICE integration allows read-only users to overwrite files via forged save callback

## Summary
Severity: High
Advisory: CVE-2026-33330
Aliases: GHSA-6c3j-f4x4-36m3
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-33330
Type: osv

## Details
FileRise is a self-hosted web file manager / WebDAV server. Prior to version 3.10.0, a broken access control issue in FileRise's ONLYOFFICE integration allows an authenticated user with read-only access to obtain a signed save callbackUrl for a file and then directly forge the ONLYOFFICE save callback to overwrite that file with attacker-controlled content. This issue has been patched in version 3.10.0.

## References
- https://github.com/error311/FileRise/releases/tag/v3.10.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33330.json
- https://github.com/error311/FileRise/security/advisories/GHSA-6c3j-f4x4-36m3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33330
- https://github.com/error311/FileRise/commit/3871f9fd1661688bed4f7dd23912be0ebf50973c
