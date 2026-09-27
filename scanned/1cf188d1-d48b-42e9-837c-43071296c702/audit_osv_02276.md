# [C] ALPINE-CVE-2021-3781

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-3781
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-02-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3781
Type: osv

## Affected
- Alpine:v3.13: `ghostscript` — affected >=0 <9.53.3-r1
- Alpine:v3.14: `ghostscript` — affected >=0 <9.54-r1
- Alpine:v3.15: `ghostscript` — affected >=0 <9.54-r1
- Alpine:v3.16: `ghostscript` — affected >=0 <9.54-r1
- Alpine:v3.17: `ghostscript` — affected >=0 <9.54-r1
- Alpine:v3.18: `ghostscript` — affected >=0 <9.54-r1
- Alpine:v3.19: `ghostscript` — affected >=0 <9.54-r1
- Alpine:v3.20: `ghostscript` — affected >=0 <9.54-r1
- Alpine:v3.21: `ghostscript` — affected >=0 <9.54-r1
- Alpine:v3.22: `ghostscript` — affected >=0 <9.54-r1
- Alpine:v3.23: `ghostscript` — affected >=0 <9.54-r1

## Details
A trivial sandbox (enabled with the `-dSAFER` option) escape flaw was found in the ghostscript interpreter by injecting a specially crafted pipe command. This flaw allows a specially crafted document to execute arbitrary commands on the system in the context of the ghostscript interpreter. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3781
