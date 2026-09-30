# [H] Untrusted Search Path in SumatraPDF Reader (explorer.exe on Windows)

## Summary
Severity: High
Advisory: CVE-2026-25880
Aliases: GHSA-5x4h-247q-px37
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-09
Source: https://osv.dev/vulnerability/CVE-2026-25880
Type: osv

## Details
SumatraPDF is a multi-format reader for Windows. In 3.5.2 and earlier, the PDF reader allows execution of a malicious binary (explorer.exe) located in the same directory as the opened PDF when the user clicks File → “Show in folder”. This behavior leads to arbitrary code execution on the victim’s system with the privileges of the current user, without any warning or user interaction beyond the menu click.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25880.json
- https://github.com/sumatrapdfreader/sumatrapdf/security/advisories/GHSA-5x4h-247q-px37
- https://nvd.nist.gov/vuln/detail/CVE-2026-25880
