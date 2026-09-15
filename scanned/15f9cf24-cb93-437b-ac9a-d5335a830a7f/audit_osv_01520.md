# [H] ALPINE-CVE-2019-18421

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-18421
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-18421
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.12.1-r1
- Alpine:v3.11: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.13.0-r0
- Alpine:v3.8: `xen` — affected >=0 <4.10.4-r1
- Alpine:v3.9: `xen` — affected >=0 <4.11.2-r1

## Details
An issue was discovered in Xen through 4.12.x allowing x86 PV guest OS users to gain host OS privileges by leveraging race conditions in pagetable promotion and demotion operations. There are issues with restartable PV type change operations. To avoid using shadow pagetables for PV guests, Xen exposes the actual hardware pagetables to the guest. In order to prevent the guest from modifying these page tables directly, Xen keeps track of how pages are used using a type system; pages must be "promoted" before being used as a pagetable, and "demoted" before being used for any other type. Xen also allows for "recursive" promotions: i.e., an operating system promoting a page to an L4 pagetable may end up causing pages to be promoted to L3s, which may in turn cause pages to be promoted to L2s, and so on. These operations may take an arbitrarily large amount of time, and so must be re-startable. Unfortunately, making recursive pagetable promotion and demotion operations restartable is incredibly complicated, and the code contains several races which, if triggered, can cause Xen to drop or retain extra type counts, potentially allowing guests to get write access to in-use pagetables. A malicious PV guest administrator may be able to escalate their privilege to that of the host. All x86 systems with untrusted PV guests are vulnerable. HVM and PVH guests cannot exercise this vulnerability.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-18421
