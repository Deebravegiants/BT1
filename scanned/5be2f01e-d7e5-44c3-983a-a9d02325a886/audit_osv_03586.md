# [H] ALPINE-CVE-2026-32942

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-32942
Ecosystem: Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-32942
Type: osv

## Affected
- Alpine:v3.24: `pjproject` — affected >=0 <2.17-r0

## Details
PJSIP is a free and open source multimedia communication library written in C. Versions 2.16 and below contain a  heap use-after-free vulnerability in the ICE session that occurs when there are race conditions between session destruction and the callbacks. This issue has been fixed in version 2.17.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-32942
