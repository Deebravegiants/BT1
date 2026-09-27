# [H] CVE-2026-42171

## Summary
Severity: High
Advisory: CVE-2026-42171
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-42171
Type: osv

## Details
NSIS (Nullsoft Scriptable Install System) 3.06.1 before 3.12 sometimes uses the Low IL temp directory when executing as SYSTEM, allowing local attackers to gain privileges (if they can cause my_GetTempFileName to return 0, as shown in the references).

## References
- https://github.com/NSIS-Dev/nsis/blob/7359413009afd4f0fff472d841fc2f2cc0e0a5f8/Source/exehead/util.c#L475-L484
- https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-gettempfilename
- https://nsis.sourceforge.io/Docs/AppendixF.html#v3.12-cl
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42171.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-42171
- https://github.com/NSIS-Dev/nsis/commit/8e6f02205d5f22da6c7855dbfe59b2af667330ca
