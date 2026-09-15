# [M] ALPINE-CVE-2022-42317

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42317
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42317
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
Xenstore: guests can let run xenstored out of memory T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Malicious guests can cause xenstored to allocate vast amounts of memory, eventually resulting in a Denial of Service (DoS) of xenstored. There are multiple ways how guests can cause large memory allocations in xenstored: - - by issuing new requests to xenstored without reading the responses, causing the responses to be buffered in memory - - by causing large number of watch events to be generated via setting up multiple xenstore watches and then e.g. deleting many xenstore nodes below the watched path - - by creating as many nodes as allowed with the maximum allowed size and path length in as many transactions as possible - - by accessing many nodes inside a transaction

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42317
