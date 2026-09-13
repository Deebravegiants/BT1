# [H] LORIS has a path traversal in FilesDownloadHandler

## Summary
Severity: High
Advisory: CVE-2026-35446
Aliases: GHSA-47jj-7xfg-8759
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-35446
Type: osv

## Details
LORIS (Longitudinal Online Research and Imaging System) is a self-hosted web application that provides data- and project-management for neuroimaging research. From 24.0.0 to before 27.0.3 and 28.0.1, an incorrect order of operations in the FilesDownloadHandler could result in an attacker escaping the intended download directories. This vulnerability is fixed in 27.0.3 and 28.0.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35446.json
- https://github.com/aces/Loris/security/advisories/GHSA-47jj-7xfg-8759
- https://nvd.nist.gov/vuln/detail/CVE-2026-35446
