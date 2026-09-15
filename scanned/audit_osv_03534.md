# [M] ALPINE-CVE-2026-27199

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-27199
Ecosystem: Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-02-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-27199
Type: osv

## Affected
- Alpine:v3.24: `py3-werkzeug` — affected >=0 <3.1.6-r0

## Details
Werkzeug is a comprehensive WSGI web application library. Versions 3.1.5 and below, the safe_join function allows Windows device names as filenames if preceded by other path segments. This was previously reported as GHSA-hgf8-39gv-g3f2, but the added filtering failed to account for the fact that safe_join accepts paths with multiple segments, such as example/NUL. The function send_from_directory uses safe_join to safely serve files at user-specified paths under a directory. If the application is running on Windows, and the requested path ends with a special device name, the file will be opened successfully, but reading will hang indefinitely. This issue has been fixed in version 3.1.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-27199
