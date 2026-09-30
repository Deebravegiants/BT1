# [M] ALPINE-CVE-2017-14317

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-14317
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.6 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-09-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-14317
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.11: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.12: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.13: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.14: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.15: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.16: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.17: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.18: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.19: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.20: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.21: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.22: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.23: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.24: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.3: `xen` — affected >=0 <4.6.3-r9
- Alpine:v3.4: `xen` — affected >=0 <4.6.3-r11
- Alpine:v3.5: `xen` — affected >=0 <4.7.2-r2
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r1
- Alpine:v3.7: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.8: `xen` — affected >=0 <4.9.0-r4
- Alpine:v3.9: `xen` — affected >=0 <4.9.0-r4

## Details
A domain cleanup issue was discovered in the C xenstore daemon (aka cxenstored) in Xen through 4.9.x. When shutting down a VM with a stubdomain, a race in cxenstored may cause a double-free. The xenstored daemon may crash, resulting in a DoS of any parts of the system relying on it (including domain creation / destruction, ballooning, device changes, etc.).

## References
- https://security.alpinelinux.org/vuln/CVE-2017-14317
