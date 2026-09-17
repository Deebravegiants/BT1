# [M] ALPINE-CVE-2014-4616

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2014-4616
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2014-4616
Type: osv

## Affected
- Alpine:v3.4: `python` — affected >=2.7.0 <2.7.7-r0
- Alpine:v3.5: `python2` — affected >=0 <2.7.7-r0
- Alpine:v3.6: `python2` — affected >=0 <2.7.7-r0

## Details
Array index error in the scanstring function in the _json module in Python 2.7 through 3.5 and simplejson before 2.6.1 allows context-dependent attackers to read arbitrary process memory via a negative index value in the idx argument to the raw_decode function.

## References
- https://security.alpinelinux.org/vuln/CVE-2014-4616
