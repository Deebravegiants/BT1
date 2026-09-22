# [H] ALPINE-CVE-2019-6467

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-6467
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6467
Type: osv

## Affected
- Alpine:v3.10: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.11: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.12: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.13: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.14: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.15: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.16: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.17: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.18: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.19: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.20: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.21: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.22: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.23: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.24: `bind` — affected >=9.12.0 <9.14.1-r0
- Alpine:v3.6: `bind` — affected >=9.12.0 <9.11.6_p1-r0
- Alpine:v3.7: `bind` — affected >=9.12.0 <9.11.6_p1-r0
- Alpine:v3.8: `bind` — affected >=9.12.0 <9.12.4_p1-r0
- Alpine:v3.9: `bind` — affected >=9.12.0 <9.12.4_p1-r0

## Details
A programming error in the nxdomain-redirect feature can cause an assertion failure in query.c if the alternate namespace used by nxdomain-redirect is a descendant of a zone that is served locally. The most likely scenario where this might occur is if the server, in addition to performing NXDOMAIN redirection for recursive clients, is also serving a local copy of the root zone or using mirroring to provide the root zone, although other configurations are also possible. Versions affected: BIND 9.12.0-> 9.12.4, 9.14.0. Also affects all releases in the 9.13 development branch.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6467
