# [H] ALPINE-CVE-2019-18934

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18934
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2019-11-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18934
Type: osv

## Affected
- Alpine:v3.10: `unbound` — affected >=1.6.4 <1.9.1-r4
- Alpine:v3.11: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.12: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.13: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.14: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.15: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.16: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.17: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.18: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.19: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.20: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.21: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.22: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.23: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.24: `unbound` — affected >=1.6.4 <1.9.5-r0
- Alpine:v3.8: `unbound` — affected >=1.6.4 <1.7.3-r2
- Alpine:v3.9: `unbound` — affected >=1.6.4 <1.8.3-r3

## Details
Unbound 1.6.4 through 1.9.4 contain a vulnerability in the ipsec module that can cause shell code execution after receiving a specially crafted answer. This issue can only be triggered if unbound was compiled with `--enable-ipsecmod` support, and ipsecmod is enabled and used in the configuration.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18934
