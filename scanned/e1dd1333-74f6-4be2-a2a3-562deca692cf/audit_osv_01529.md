# [H] ALPINE-CVE-2019-18874

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18874
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18874
Type: osv

## Affected
- Alpine:v3.23: `py3-psutil` — affected >=0 <5.6.7-r0
- Alpine:v3.24: `py3-psutil` — affected >=0 <5.6.7-r0

## Details
psutil (aka python-psutil) through 5.6.5 can have a double free. This occurs because of refcount mishandling within a while or for loop that converts system data into a Python object.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18874
