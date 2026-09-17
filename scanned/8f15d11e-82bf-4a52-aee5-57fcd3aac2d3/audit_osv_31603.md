# [C] Notepad++ < 8.8.9 WinGUp Updater Lacks Update Integrity Verification

## Summary
Severity: Critical
Advisory: CVE-2025-15556
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2025-15556
Type: osv

## Details
Notepad++ versions prior to 8.8.9, when using the WinGUp updater, contain an update integrity verification vulnerability where downloaded update metadata and installers are not cryptographically verified. An attacker able to intercept or redirect update traffic can cause the updater to download and execute an attacker-controlled installer, resulting in arbitrary code execution with the privileges of the user.

## References
- https://github.com/notepad-plus-plus
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2025-15556
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15556.json
- https://notepad-plus-plus.org//news//clarification-security-incident/
- https://notepad-plus-plus.org/news/hijacked-incident-info-update/
- https://nvd.nist.gov/vuln/detail/CVE-2025-15556
- https://www.vulncheck.com/advisories/notepad-plus-plus-wingup-updater-lacks-update-integrity-verification
- https://community.notepad-plus-plus.org/topic/27298/notepad-v8-8-9-vulnerability-fix
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/bcf2aa68ef414338d717e20e059459570ed6c5ab
- https://github.com/notepad-plus-plus/wingup/commit/ce0037549995ed0396cc363544d14b3425614fdb
