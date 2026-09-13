# [H] ALPINE-CVE-2016-2776

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-2776
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-09-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-2776
Type: osv

## Affected
- Alpine:v3.2: `bind` — affected >=0 <9.10.4_p3
- Alpine:v3.3: `bind` — affected >=0 <9.10.4_p3-r0

## Details
buffer.c in named in ISC BIND 9 before 9.9.9-P3, 9.10.x before 9.10.4-P3, and 9.11.x before 9.11.0rc3 does not properly construct responses, which allows remote attackers to cause a denial of service (assertion failure and daemon exit) via a crafted query.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-2776
