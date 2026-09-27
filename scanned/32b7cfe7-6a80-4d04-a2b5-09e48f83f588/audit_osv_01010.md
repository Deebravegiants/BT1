# [M] ALPINE-CVE-2018-15470

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-15470
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15470
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.11: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.12: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.13: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.14: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.15: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.16: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.17: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.18: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.19: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.20: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.21: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.22: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.11.1-r0
- Alpine:v3.6: `xen` — affected >=0 <4.8.5-r0
- Alpine:v3.7: `xen` — affected >=0 <4.9.3-r0
- Alpine:v3.8: `xen` — affected >=0 <4.10.1-r3
- Alpine:v3.9: `xen` — affected >=0 <4.11.1-r0

## Details
An issue was discovered in Xen through 4.11.x. The logic in oxenstored for handling writes depended on the order of evaluation of expressions making up a tuple. As indicated in section 7.7.3 "Operations on data structures" of the OCaml manual, the order of evaluation of subexpressions is not specified. In practice, different implementations behave differently. Thus, oxenstored may not enforce the configured quota-maxentity. This allows a malicious or buggy guest to write as many xenstore entries as it wishes, causing unbounded memory usage in oxenstored. This can lead to a system-wide DoS.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15470
