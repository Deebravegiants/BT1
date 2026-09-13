# [M] ALPINE-CVE-2025-66221

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-66221
Ecosystem: Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-66221
Type: osv

## Affected
- Alpine:v3.24: `py3-werkzeug` — affected >=0 <3.1.4-r0

## Details
Werkzeug is a comprehensive WSGI web application library. Prior to version 3.1.4, Werkzeug's safe_join function allows path segments with Windows device names. On Windows, there are special device names such as CON, AUX, etc that are implicitly present and readable in every directory. send_from_directory uses safe_join to safely serve files at user-specified paths under a directory. If the application is running on Windows, and the requested path ends with a special device name, the file will be opened successfully, but reading will hang indefinitely. This issue has been patched in version 3.1.4.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-66221
