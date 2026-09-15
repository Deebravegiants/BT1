# [H] ALPINE-CVE-2026-76957

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-76957
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-76957
Type: osv

## Affected
- Alpine:v3.21: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.22: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.23: `expat` — affected >=0 <2.8.4-r0
- Alpine:v3.24: `expat` — affected >=0 <2.8.4-r0

## Details
libexpat before 2.8.4 lacks handler call depth tracking with custom encoding callbacks. Thus, a use-after-free can occur. NOTE: this is similar to CVE-2026-50219, CVE-2026-56131 and CVE-2026-56412.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-76957
