# [H] Notepad++: Stack Buffer Overflow in expandNppEnvironmentStrs

## Summary
Severity: High
Advisory: CVE-2026-54758
Aliases: GHSA-gv94-327x-2gc5
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-54758
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Prior to 8.9.7, the expandNppEnvironmentStrs function in PowerEditor/src/WinControls/StaticDialog/RunDlg/RunDlg.cpp copies a Notepad++ variable name between $( and ) into the fixed-size wchar_t str[MAX_PATH] stack buffer without bounding the m loop index, allowing a name of 260 or more characters to corrupt adjacent stack data, terminate the process through __report_gsfailure, and potentially execute code. This issue is fixed in version 8.9.7.

## References
- https://github.com/notepad-plus-plus/notepad-plus-plus/releases/tag/v8.9.7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54758.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-gv94-327x-2gc5
- https://nvd.nist.gov/vuln/detail/CVE-2026-54758
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/0a9527e9f7140a2323e25d14e362b46ee0efc3db
