# [M] ALPINE-CVE-2020-26137

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-26137
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-09-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-26137
Type: osv

## Affected
- Alpine:v3.13: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.14: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.15: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.16: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.17: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.18: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.19: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.20: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.21: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.22: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.23: `py3-urllib3` — affected >=0 <1.25.9-r0
- Alpine:v3.24: `py3-urllib3` — affected >=0 <1.25.9-r0

## Details
urllib3 before 1.25.9 allows CRLF injection if the attacker controls the HTTP request method, as demonstrated by inserting CR and LF control characters in the first argument of putrequest(). NOTE: this is similar to CVE-2020-26116.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-26137
