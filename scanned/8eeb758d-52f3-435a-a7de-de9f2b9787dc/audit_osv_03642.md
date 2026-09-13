# [H] ALPINE-CVE-2026-3644

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-3644
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-3644
Type: osv

## Affected
- Alpine:v3.21: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.24: `python3` — affected >=0 <3.14.5-r0

## Details
The fix for CVE-2026-0672, which rejected control characters in http.cookies.Morsel, was incomplete. The Morsel.update(), |= operator, and unpickling paths were not patched, allowing control characters to bypass input validation. Additionally, BaseCookie.js_output() lacked the output validation applied to BaseCookie.output().

## References
- https://security.alpinelinux.org/vuln/CVE-2026-3644
