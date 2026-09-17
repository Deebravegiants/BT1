# [H] ALPINE-CVE-2016-8864

## Summary
Severity: High
Advisory: ALPINE-CVE-2016-8864
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-02
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-8864
Type: osv

## Affected
- Alpine:v3.2: `bind` — affected >=9.0.0 <9.10.4_p4-r0
- Alpine:v3.3: `bind` — affected >=9.0.0 <9.10.4_p4-r0

## Details
named in ISC BIND 9.x before 9.9.9-P4, 9.10.x before 9.10.4-P4, and 9.11.x before 9.11.0-P1 allows remote attackers to cause a denial of service (assertion failure and daemon exit) via a DNAME record in the answer section of a response to a recursive query, related to db.c and resolver.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-8864
