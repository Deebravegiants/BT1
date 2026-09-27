# [H] Improper Control of Generation of Code ('Code Injection') in dail8859/NotepadNext

## Summary
Severity: High
Advisory: CVE-2026-42214
Aliases: GHSA-m5fq-c9x5-w54g
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-42214
Type: osv

## Details
Notepad Next is a cross-platform, reimplementation of Notepad++. Prior to version 0.14, NotepadNext's detectLanguageFromExtension() function interpolates a file's extension directly into a Lua script without sanitization. An attacker can craft a filename whose extension contains Lua code, which executes automatically when the victim opens the file in NotepadNext. Because luaL_openlibs() is called unconditionally, the full os, io, and package libraries are available to the injected code, enabling arbitrary command execution. This issue has been patched in version 0.14.

## References
- https://github.com/dail8859/NotepadNext/releases/tag/v0.14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42214.json
- https://github.com/dail8859/NotepadNext/security/advisories/GHSA-m5fq-c9x5-w54g
- https://nvd.nist.gov/vuln/detail/CVE-2026-42214
- https://github.com/dail8859/NotepadNext/commit/f3ca1b10aca52f05fd7f4f5ebf9b566d6cd95ccc
