# [H] SumatraPDF has an Untrusted Search Path in sumatrapdf/src/AppTools.cpp

## Summary
Severity: High
Advisory: CVE-2026-23512
Aliases: GHSA-rqg5-gj63-x4mv
CVSS: 8.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-23512
Type: osv

## Details
SumatraPDF is a multi-format reader for Windows. In 3.5.2 and earlier, there is a Untrusted Search Path vulnerability when Advanced Options setting is trigger. The application executes notepad.exe without specifying an absolute path when using the Advanced Options setting. On Windows, this allows execution of a malicious notepad.exe placed in the application's installation directory, leading to arbitrary code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23512.json
- https://github.com/sumatrapdfreader/sumatrapdf/security/advisories/GHSA-rqg5-gj63-x4mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-23512
- https://github.com/sumatrapdfreader/sumatrapdf/commit/2762e02a8cd7cb779c934a44257aac56ab7de673
