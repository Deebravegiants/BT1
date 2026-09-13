# [H] ALPINE-CVE-2018-14647

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-14647
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-09-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14647
Type: osv

## Affected
- Alpine:v3.10: `python2` — affected >=0 <2.7.16-r0
- Alpine:v3.11: `python2` — affected >=0 <2.7.16-r0
- Alpine:v3.12: `python2` — affected >=0 <2.7.16-r0
- Alpine:v3.7: `python2` — affected >=0 <2.7.15-r2
- Alpine:v3.8: `python2` — affected >=0 <2.7.15-r2
- Alpine:v3.9: `python2` — affected >=0 <2.7.16-r0
- Alpine:v3.6: `python3` — affected >=0 <3.6.8-r0
- Alpine:v3.7: `python3` — affected >=0 <3.6.8-r0
- Alpine:v3.8: `python3` — affected >=0 <3.6.8-r0

## Details
Python's elementtree C accelerator failed to initialise Expat's hash salt during initialization. This could make it easy to conduct denial of service attacks against Expat by constructing an XML document that would cause pathological hash collisions in Expat's internal data structures, consuming large amounts CPU and RAM. The vulnerability exists in Python versions 3.7.0, 3.6.0 through 3.6.6, 3.5.0 through 3.5.6, 3.4.0 through 3.4.9, 2.7.0 through 2.7.15.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14647
