# [H] ALPINE-CVE-2017-3141

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-3141
Ecosystem: Alpine:v3.6, Alpine:v3.7
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-3141
Type: osv

## Affected
- Alpine:v3.6: `bind` — affected >=9.2.6 <9.11.3-r0
- Alpine:v3.7: `bind` — affected >=9.2.6 <9.11.3-r0

## Details
The BIND installer on Windows uses an unquoted service path which can enable a local user to achieve privilege escalation if the host file system permissions allow this. Affects BIND 9.2.6-P2->9.2.9, 9.3.2-P1->9.3.6, 9.4.0->9.8.8, 9.9.0->9.9.10, 9.10.0->9.10.5, 9.11.0->9.11.1, 9.9.3-S1->9.9.10-S1, 9.10.5-S1.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-3141
