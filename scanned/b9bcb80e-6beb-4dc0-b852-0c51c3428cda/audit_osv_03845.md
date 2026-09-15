# [M] ALPINE-CVE-2026-56131

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-56131
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-56131
Type: osv

## Affected
- Alpine:v3.21: `expat` — affected >=0 <2.8.2-r0
- Alpine:v3.22: `expat` — affected >=0 <2.8.2-r0
- Alpine:v3.23: `expat` — affected >=0 <2.8.2-r0
- Alpine:v3.24: `expat` — affected >=0 <2.8.2-r0

## Details
libexpat before 2.8.2 lacks handler call depth tracking for calls to XML_ResumeParser from within handlers in cases of a policy violation. Thus, a use-after-free can occur (similar to the CVE-2026-50219 situation).

## References
- https://security.alpinelinux.org/vuln/CVE-2026-56131
