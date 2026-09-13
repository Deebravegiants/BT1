# [H] ALPINE-CVE-2022-42320

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-42320
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42320
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.16: `xen` — affected >=0 <4.16.3-r0
- Alpine:v3.17: `xen` — affected >=0 <4.16.3-r0
- Alpine:v3.18: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.17.0-r0

## Details
Xenstore: Guests can get access to Xenstore nodes of deleted domains Access rights of Xenstore nodes are per domid. When a domain is gone, there might be Xenstore nodes left with access rights containing the domid of the removed domain. This is normally no problem, as those access right entries will be corrected when such a node is written later. There is a small time window when a new domain is created, where the access rights of a past domain with the same domid as the new one will be regarded to be still valid, leading to the new domain being able to get access to a node which was meant to be accessible by the removed domain. For this to happen another domain needs to write the node before the newly created domain is being introduced to Xenstore by dom0.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42320
