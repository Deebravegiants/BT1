# [H] ALPINE-CVE-2024-45720

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-45720
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-45720
Type: osv

## Affected
- Alpine:v3.18: `subversion` — affected >=0 <1.14.5-r0
- Alpine:v3.19: `subversion` — affected >=0 <1.14.5-r0
- Alpine:v3.20: `subversion` — affected >=0 <1.14.5-r0
- Alpine:v3.21: `subversion` — affected >=0 <1.14.4-r0
- Alpine:v3.22: `subversion` — affected >=0 <1.14.4-r0
- Alpine:v3.23: `subversion` — affected >=0 <1.14.4-r0
- Alpine:v3.24: `subversion` — affected >=0 <1.14.4-r0

## Details
On Windows platforms, a "best fit" character encoding conversion of command line arguments to Subversion's executables (e.g., svn.exe, etc.) may lead to unexpected command line argument interpretation, including argument injection and execution of other programs, if a specially crafted command line argument string is processed.

All versions of Subversion up to and including Subversion 1.14.3 are affected on Windows platforms only. Users are recommended to upgrade to version Subversion 1.14.4, which fixes this issue.

Subversion is not affected on UNIX-like platforms.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-45720
