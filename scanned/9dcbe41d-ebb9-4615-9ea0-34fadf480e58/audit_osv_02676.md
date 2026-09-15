# [M] ALPINE-CVE-2022-42323

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42323
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42323
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
Xenstore: Cooperating guests can create arbitrary numbers of nodes T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Since the fix of XSA-322 any Xenstore node owned by a removed domain will be modified to be owned by Dom0. This will allow two malicious guests working together to create an arbitrary number of Xenstore nodes. This is possible by domain A letting domain B write into domain A's local Xenstore tree. Domain B can then create many nodes and reboot. The nodes created by domain B will now be owned by Dom0. By repeating this process over and over again an arbitrary number of nodes can be created, as Dom0's number of nodes isn't limited by Xenstore quota.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42323
