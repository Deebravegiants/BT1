# [H] ALPINE-CVE-2020-29479

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-29479
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-29479
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=0 <4.13.2-r3
- Alpine:v3.12: `xen` — affected >=0 <4.13.2-r3
- Alpine:v3.13: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.14: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.15: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.16: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.17: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.18: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.19: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.20: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.21: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.22: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.23: `xen` — affected >=0 <4.14.1-r0
- Alpine:v3.24: `xen` — affected >=0 <4.14.1-r0

## Details
An issue was discovered in Xen through 4.14.x. In the Ocaml xenstored implementation, the internal representation of the tree has special cases for the root node, because this node has no parent. Unfortunately, permissions were not checked for certain operations on the root node. Unprivileged guests can get and modify permissions, list, and delete the root node. (Deleting the whole xenstore tree is a host-wide denial of service.) Achieving xenstore write access is also possible. All systems using oxenstored are vulnerable. Building and using oxenstored is the default in the upstream Xen distribution, if the Ocaml compiler is available. Systems using C xenstored are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-29479
