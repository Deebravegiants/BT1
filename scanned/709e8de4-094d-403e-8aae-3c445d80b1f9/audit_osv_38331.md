# [H] CVE-2026-38972

## Summary
Severity: High
Advisory: CVE-2026-38972
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-38972
Type: osv

## Details
Notepad3 through 6.25.822.1 contains a DLL search-order hijacking vulnerability in the About-dialog code path in src/Notepad3.c. The application calls LoadLibrary(L"MSFTEDIT.DLL") with a bare DLL name, which allows a local attacker to place a malicious MSFTEDIT.DLL in the application directory or another preferred DLL search location and achieve arbitrary code execution in the context of the user when the About dialog is opened.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/38xxx/CVE-2026-38972.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-38972
- https://github.com/rizonesoft/Notepad3/issues/5605
- https://github.com/rizonesoft/Notepad3/pull/5606
- https://github.com/rizonesoft/Notepad3
