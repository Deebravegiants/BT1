# [H] ALPINE-CVE-2026-34980

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-34980
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-34980
Type: osv

## Affected
- Alpine:v3.20: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.21: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.22: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.23: `cups` — affected >=0 <2.4.18-r0
- Alpine:v3.24: `cups` — affected >=0 <2.4.18-r0

## Details
OpenPrinting CUPS is an open source printing system for Linux and other Unix-like operating systems. In versions 2.4.16 and prior, in a network-exposed cupsd with a shared target queue, an unauthorized client can send a Print-Job to that shared PostScript queue without authentication. The server accepts a page-border value supplied as textWithoutLanguage, preserves an embedded newline through option escaping and reparse, and then reparses the resulting second-line PPD: text as a trusted scheduler control record. A follow-up raw print job can therefore make the server execute an attacker-chosen existing binary such as /usr/bin/vim as lp. At time of publication, there are no publicly available patches.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-34980
