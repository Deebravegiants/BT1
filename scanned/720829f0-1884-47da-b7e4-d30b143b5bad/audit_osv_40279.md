# [H] Notepad++: CVE-2026-48800 Bypass

## Summary
Severity: High
Advisory: CVE-2026-52884
Aliases: GHSA-p58x-r3c9-x9p6
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-26
Source: https://osv.dev/vulnerability/CVE-2026-52884
Type: osv

## Details
Notepad++ is a free and open-source source code editor. In v8.9.6.1, isInTrustedDirectory() does NOT canonicalize the path before checking. It uses a prefix-based check (PathIsPrefix() or equivalent) that matches paths starting with trusted directory strings. A path traversal using ..\..\ after a trusted directory prefix passes the check while resolving to an untrusted location. The CVE-2026-48800 patch adds isInTrustedDirectory() validation in Command::run() (RunDlg.cpp) before calling ShellExecute(). This function checks whether the resolved executable path is under a trusted directory.  This vulnerability is fixed in 8.9.6.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/52xxx/CVE-2026-52884.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-p58x-r3c9-x9p6
- https://nvd.nist.gov/vuln/detail/CVE-2026-52884
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/ea1508855e9c4528f6198ce9d345f13cb759ebf4
