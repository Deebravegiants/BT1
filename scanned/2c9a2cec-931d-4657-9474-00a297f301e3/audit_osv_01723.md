# [M] ALPINE-CVE-2020-11743

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-11743
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-11743
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.2-r1
- Alpine:v3.11: `xen` — affected >=0 <4.13.0-r1
- Alpine:v3.12: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.13: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.14: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.15: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.16: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.17: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.18: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.19: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.20: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.21: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.22: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.23: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.24: `xen` — affected >=0 <4.13.0-r3
- Alpine:v3.8: `xen` — affected >=0 <4.10.4-r3
- Alpine:v3.9: `xen` — affected >=0 <4.11.3-r2

## Details
An issue was discovered in Xen through 4.13.x, allowing guest OS users to cause a denial of service because of a bad error path in GNTTABOP_map_grant. Grant table operations are expected to return 0 for success, and a negative number for errors. Some misplaced brackets cause one error path to return 1 instead of a negative value. The grant table code in Linux treats this condition as success, and proceeds with incorrectly initialised state. A buggy or malicious guest can construct its grant table in such a way that, when a backend domain tries to map a grant, it hits the incorrect error path. This will crash a Linux based dom0 or backend domain.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-11743
