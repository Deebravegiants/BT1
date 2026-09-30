# [C] FileBrowser before 2.63.19 Case Sensitivity Authentication Bypass

## Summary
Severity: Critical
Advisory: CVE-2026-72836
Aliases: GHSA-576v-w77m-gr84
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/CVE-2026-72836
Type: osv

## Details
FileBrowser before 2.63.19 does not account for case-insensitive filesystems when checking home directory ownership during self-registration. When Signup and CreateUserDir are enabled and FileBrowser's root is on a case-insensitive filesystem (confirmed on Windows/NTFS), two self-registered usernames that differ only in letter case (e.g., CaseVictim and casevictim) are stored as distinct accounts but resolve to the same physical home directory, because the scope-ownership check compares the persisted scope as an exact case-sensitive string. A second registrant can therefore read, overwrite, and delete another account's files through authenticated HTTP endpoints, without needing an existing account or victim interaction.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72836.json
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-576v-w77m-gr84
- https://nvd.nist.gov/vuln/detail/CVE-2026-72836
- https://www.vulncheck.com/advisories/filebrowser-before-case-sensitivity-authentication-bypass
- https://github.com/filebrowser/filebrowser/commit/fe7efb2e6afe66774cd86a5b0a03033bd514d0c0
