# [M] ALPINE-CVE-2026-21860

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-21860
Ecosystem: Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-01-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-21860
Type: osv

## Affected
- Alpine:v3.24: `py3-werkzeug` — affected >=0 <3.1.5-r0

## Details
Werkzeug is a comprehensive WSGI web application library. Prior to version 3.1.5, Werkzeug's safe_join function allows path segments with Windows device names that have file extensions or trailing spaces. On Windows, there are special device names such as CON, AUX, etc that are implicitly present and readable in every directory. Windows still accepts them with any file extension, such as CON.txt, or trailing spaces such as CON. This issue has been patched in version 3.1.5.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-21860
