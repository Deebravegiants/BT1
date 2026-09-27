# [M] ALPINE-CVE-2022-26364

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-26364
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-06-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-26364
Type: osv

## Affected
- Alpine:v3.13: `xen` — affected >=0 <4.14.5-r1
- Alpine:v3.14: `xen` — affected >=0 <4.15.2-r1
- Alpine:v3.15: `xen` — affected >=0 <4.15.2-r1
- Alpine:v3.16: `xen` — affected >=0 <4.16.1-r1
- Alpine:v3.17: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.18: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.19: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.20: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.21: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.22: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.23: `xen` — affected >=0 <4.16.1-r2
- Alpine:v3.24: `xen` — affected >=0 <4.16.1-r2

## Details
x86 pv: Insufficient care with non-coherent mappings T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] Xen maintains a type reference count for pages, in addition to a regular reference count. This scheme is used to maintain invariants required for Xen's safety, e.g. PV guests may not have direct writeable access to pagetables; updates need auditing by Xen. Unfortunately, Xen's safety logic doesn't account for CPU-induced cache non-coherency; cases where the CPU can cause the content of the cache to be different to the content in main memory. In such cases, Xen's safety logic can incorrectly conclude that the contents of a page is safe.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-26364
