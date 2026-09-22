# [H] ALPINE-CVE-2023-43804

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-43804
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-43804
Type: osv

## Affected
- Alpine:v3.15: `py3-urllib3` — affected >=0 <1.26.17-r0
- Alpine:v3.16: `py3-urllib3` — affected >=0 <1.26.17-r0
- Alpine:v3.17: `py3-urllib3` — affected >=0 <1.26.17-r0
- Alpine:v3.18: `py3-urllib3` — affected >=0 <1.26.17-r0
- Alpine:v3.19: `py3-urllib3` — affected >=0 <1.26.17-r0
- Alpine:v3.20: `py3-urllib3` — affected >=0 <1.26.17-r0
- Alpine:v3.21: `py3-urllib3` — affected >=0 <1.26.17-r0
- Alpine:v3.22: `py3-urllib3` — affected >=0 <1.26.17-r0
- Alpine:v3.23: `py3-urllib3` — affected >=0 <1.26.17-r0
- Alpine:v3.24: `py3-urllib3` — affected >=0 <1.26.17-r0

## Details
urllib3 is a user-friendly HTTP client library for Python. urllib3 doesn't treat the `Cookie` HTTP header special or provide any helpers for managing cookies over HTTP, that is the responsibility of the user. However, it is possible for a user to specify a `Cookie` header and unknowingly leak information via HTTP redirects to a different origin if that user doesn't disable redirects explicitly. This issue has been patched in urllib3 version 1.26.17 or 2.0.5.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-43804
