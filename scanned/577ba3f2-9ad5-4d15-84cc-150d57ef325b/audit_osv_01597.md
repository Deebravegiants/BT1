# [H] ALPINE-CVE-2019-5010

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-5010
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-5010
Type: osv

## Affected
- Alpine:v3.10: `python2` — affected >=0 <2.7.15-r3
- Alpine:v3.11: `python2` — affected >=0 <2.7.15-r3
- Alpine:v3.12: `python2` — affected >=0 <2.7.15-r3
- Alpine:v3.9: `python2` — affected >=0 <2.7.15-r3
- Alpine:v3.10: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.11: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.12: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.13: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.14: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.15: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.16: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.17: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.18: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.19: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.20: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.21: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.22: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.23: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.24: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.9: `python3` — affected >=0 <3.6.8-r1
- Alpine:v3.23: `python3-tkinter` — affected >=0 <3.6.8-r1
- Alpine:v3.24: `python3-tkinter` — affected >=0 <3.6.8-r1

## Details
An exploitable denial-of-service vulnerability exists in the X509 certificate parser of Python.org Python 2.7.11 / 3.6.6. A specially crafted X509 certificate can cause a NULL pointer dereference, resulting in a denial of service. An attacker can initiate or accept TLS connections using crafted certificates to trigger this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-5010
