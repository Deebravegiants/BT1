# [H] ALPINE-CVE-2021-29376

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-29376
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-29376
Type: osv

## Affected
- Alpine:v3.12: `ircii` — affected >=0 <20210314-r0
- Alpine:v3.13: `ircii` — affected >=0 <20210314-r0
- Alpine:v3.14: `ircii` — affected >=0 <20210314-r0

## Details
ircII before 20210314 allows remote attackers to cause a denial of service (segmentation fault and client crash, disconnecting the victim from an IRC server) via a crafted CTCP UTC message.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-29376
