# [H] ALPINE-CVE-2026-28799

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-28799
Ecosystem: Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28799
Type: osv

## Affected
- Alpine:v3.24: `pjproject` — affected >=0 <2.17-r0

## Details
PJSIP is a free and open source multimedia communication library written in C. Prior to version 2.17, a heap use-after-free vulnerability exists in PJSIP's event subscription framework (evsub.c) that is triggered during presence unsubscription (SUBSCRIBE with Expires=0). This issue has been patched in version 2.17.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28799
