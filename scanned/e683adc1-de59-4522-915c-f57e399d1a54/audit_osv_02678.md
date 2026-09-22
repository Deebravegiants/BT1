# [M] ALPINE-CVE-2022-42325

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42325
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42325
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=4.9.0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=4.9.0 <4.15.4-r0
- Alpine:v3.16: `xen` — affected >=4.9.0 <4.16.3-r0
- Alpine:v3.17: `xen` — affected >=4.9.0 <4.16.3-r0
- Alpine:v3.18: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.19: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.20: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.21: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.22: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.23: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.24: `xen` — affected >=4.9.0 <4.17.0-r0

## Details
Xenstore: Guests can create arbitrary number of nodes via transactions T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] In case a node has been created in a transaction and it is later deleted in the same transaction, the transaction will be terminated with an error. As this error is encountered only when handling the deleted node at transaction finalization, the transaction will have been performed partially and without updating the accounting information. This will enable a malicious guest to create arbitrary number of nodes.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42325
