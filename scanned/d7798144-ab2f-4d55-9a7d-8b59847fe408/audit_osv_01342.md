# [H] ALPINE-CVE-2019-11455

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-11455
Ecosystem: Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2019-04-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-11455
Type: osv

## Affected
- Alpine:v3.7: `monit` — affected >=0 <5.24.0-r2
- Alpine:v3.8: `monit` — affected >=0 <5.25.2-r0
- Alpine:v3.9: `monit` — affected >=0 <5.25.2-r1

## Details
A buffer over-read in Util_urlDecode in util.c in Tildeslash Monit before 5.25.3 allows a remote authenticated attacker to retrieve the contents of adjacent memory via manipulation of GET or POST parameters. The attacker can also cause a denial of service (application outage).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-11455
