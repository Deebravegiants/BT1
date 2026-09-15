# [H] notepad-plus-plus - DLL Hijacking

## Summary
Severity: High
Advisory: CVE-2022-32168
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-28
Source: https://osv.dev/vulnerability/CVE-2022-32168
Type: osv

## Details
Notepad++ versions 8.4.1 and before are vulnerable to DLL hijacking where an attacker can replace the vulnerable dll (UxTheme.dll) with his own dll and run arbitrary code in the context of Notepad++.

## References
- https://www.mend.io/vulnerability-database/CVE-2022-32168
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32168.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32168
- https://github.com/notepad-plus-plus/notepad-plus-plus/commit/85d7215d9b3e0d5a8433fc31aec4f2966821051e
