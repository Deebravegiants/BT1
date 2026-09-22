# [H] Tabby: Drag-and-drop path injection still allows RCE via shell command substitution (incomplete fix for CVE-2026-45038)

## Summary
Severity: High
Advisory: CVE-2026-46709
Aliases: GHSA-mq9v-2pgm-fxgh
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-46709
Type: osv

## Details
Tabby (formerly Terminus) is a highly configurable terminal emulator. Prior to 1.0.234, Tabby inserts dropped file paths from tabby-electron/src/pathDrop.ts into the active shell without neutralizing command substitution metacharacters such as $(…) and `…`, so the incomplete CVE-2026-45038 fix for control characters still allows code execution when the victim presses Enter. This issue is fixed in version 1.0.234.

## References
- https://github.com/Eugeny/tabby/releases/tag/v1.0.234
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46709.json
- https://github.com/Eugeny/tabby/security/advisories/GHSA-mq9v-2pgm-fxgh
- https://nvd.nist.gov/vuln/detail/CVE-2026-46709
- https://github.com/Eugeny/tabby/commit/e151472b951bbd472ddc0545ec8656e4c0f352da
