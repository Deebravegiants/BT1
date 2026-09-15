# [H] Notepad++ has an Untrusted Search Path

## Summary
Severity: High
Advisory: CVE-2026-25926
Aliases: GHSA-rjvm-fcxw-2jxq
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-18
Source: https://osv.dev/vulnerability/CVE-2026-25926
Type: osv

## Details
Notepad++ is a free and open-source source code editor. An Unsafe Search Path vulnerability (CWE-426) exists in versions prior to 8.9.2 when launching Windows Explorer without an absolute executable path. This may allow execution of a malicious explorer.exe if an attacker can control the process working directory. Under certain conditions, this could lead to arbitrary code execution in the context of the running application. Version 8.9.2 patches the issue.

## References
- https://github.com/notepad-plus-plus/notepad-plus-plus/releases/tag/v8.9.2
- https://notepad-plus-plus.org/news/v892-released
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25926.json
- https://github.com/notepad-plus-plus/notepad-plus-plus/security/advisories/GHSA-rjvm-fcxw-2jxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-25926
