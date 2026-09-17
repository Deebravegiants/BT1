# [H] ALPINE-CVE-2020-6582

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-6582
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-6582
Type: osv

## Affected
- Alpine:v3.13: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.14: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.15: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.16: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.18: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.19: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.20: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.21: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.22: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.23: `nrpe` — affected >=0 <4.0.0-r0
- Alpine:v3.24: `nrpe` — affected >=0 <4.0.0-r0

## Details
Nagios NRPE 3.2.1 has a Heap-Based Buffer Overflow, as demonstrated by interpretation of a small negative number as a large positive number during a bzero call.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-6582
