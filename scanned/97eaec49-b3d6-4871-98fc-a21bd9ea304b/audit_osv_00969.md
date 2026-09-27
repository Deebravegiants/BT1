# [C] ALPINE-CVE-2018-14349

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2018-14349
Ecosystem: Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14349
Type: osv

## Affected
- Alpine:v3.5: `mutt` — affected >=0 <1.10.1-r0
- Alpine:v3.6: `mutt` — affected >=0 <1.10.1-r0
- Alpine:v3.7: `mutt` — affected >=0 <1.10.1-r0
- Alpine:v3.8: `mutt` — affected >=0 <1.10.1-r0

## Details
An issue was discovered in Mutt before 1.10.1 and NeoMutt before 2018-07-16. imap/command.c mishandles a NO response without a message.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14349
