# [H] Kakoune has a Critical RCE via Autorestore Backup Filename Injection

## Summary
Severity: High
Advisory: CVE-2026-48120
Aliases: GHSA-h99r-h8cp-vwcq
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-08-07
Source: https://osv.dev/vulnerability/CVE-2026-48120
Type: osv

## Details
Kakoune is a code editor. Prior to version 2026.05.21, the bundled, enabled by default, `autorestore.kak` script can be exploited by malicious backup files leading to arbitrary kakoune and shell commands being executed by simply opening a file. Kakoune 2026.05.21 fixes the issue. As a workaround, add `autorestore-disable` to the user kakrc will disable the autorestore feature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48120.json
- https://github.com/mawww/kakoune/security/advisories/GHSA-h99r-h8cp-vwcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-48120
- https://github.com/mawww/kakoune/commit/25c7b13b244fd1ddacc63ecfe1784b5ebc2ba825
