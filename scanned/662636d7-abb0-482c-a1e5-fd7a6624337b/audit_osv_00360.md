# [C] ALPINE-CVE-2017-1000158

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-1000158
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000158
Type: osv

## Affected
- Alpine:v3.4: `python` — affected >=3.4.0 <2.7.14-r0
- Alpine:v3.5: `python2` — affected >=0 <2.7.14-r0
- Alpine:v3.6: `python2` — affected >=0 <2.7.14-r0

## Details
CPython (aka Python) up to 2.7.13 is vulnerable to an integer overflow in the PyString_DecodeEscape function in stringobject.c, resulting in heap-based buffer overflow (and possible arbitrary code execution)

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000158
