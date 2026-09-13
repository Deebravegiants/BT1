# [M] ALPINE-CVE-2020-11740

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-11740
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-11740
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=3.2.0 <4.12.2-r1
- Alpine:v3.11: `xen` — affected >=3.2.0 <4.13.0-r1
- Alpine:v3.12: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.13: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.14: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.15: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.16: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.17: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.18: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.19: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.20: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.21: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.22: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.23: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.24: `xen` — affected >=3.2.0 <4.13.0-r3
- Alpine:v3.8: `xen` — affected >=3.2.0 <4.10.4-r3
- Alpine:v3.9: `xen` — affected >=3.2.0 <4.11.3-r2

## Details
An issue was discovered in xenoprof in Xen through 4.13.x, allowing guest OS users (without active profiling) to obtain sensitive information about other guests. Unprivileged guests can request to map xenoprof buffers, even if profiling has not been enabled for those guests. These buffers were not scrubbed.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-11740
