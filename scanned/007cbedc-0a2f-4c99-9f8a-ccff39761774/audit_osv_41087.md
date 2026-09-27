# [M] Vim: PowerShell Command Injection via Unescaped Filename in zip.vim Extraction

## Summary
Severity: Medium
Advisory: CVE-2026-57453
Aliases: GHSA-x5fg-h5w9-9frf
CVSS: 6.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:L)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-57453
Type: osv

## Details
Vim is an open source, command line text editor. From 9.1.1784 until 9.2.0678, when the bundled zip plugin autoload/zip.vim falls back to PowerShell to browse, read, extract, update or delete entries in a zip archive, it builds the PowerShell command by inserting archive entry names that are quoted only for the shell, not for PowerShell. A crafted entry name can break out of the intended string context and cause PowerShell to execute arbitrary commands with the privileges of the user running Vim, triggered by opening, viewing or extracting the archive. This vulnerability is fixed in 9.2.0678.

## References
- https://github.com/vim/vim/releases/tag/v9.2.0678
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57453.json
- https://github.com/vim/vim/security/advisories/GHSA-x5fg-h5w9-9frf
- https://nvd.nist.gov/vuln/detail/CVE-2026-57453
- https://github.com/vim/vim/commit/b2cc9be119d51212bf0d3f2a99
