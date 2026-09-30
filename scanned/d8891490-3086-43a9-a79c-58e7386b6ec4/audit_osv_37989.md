# [H] Coolify LocalFileVolume fs_path command injection enables RCE

## Summary
Severity: High
Advisory: CVE-2026-34153
Aliases: GHSA-46hp-7m8g-7622
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-34153
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, LocalFileVolume::saveStorageOnServer builds shell commands using unescaped fs_path and parent_dir values before validation, and submitFileStorage does not validate the user-controlled file-mount path before creating a volume, allowing an authenticated user who can add file storage to execute commands when the storage is saved. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34153.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-46hp-7m8g-7622
- https://nvd.nist.gov/vuln/detail/CVE-2026-34153
- https://github.com/coollabsio/coolify/commit/3fdce06b654fa3b7b4be59c0faaab6b4546c78de
- https://github.com/coollabsio/coolify/pull/9176
