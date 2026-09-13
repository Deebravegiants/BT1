# [M] ALPINE-CVE-2021-28698

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28698
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28698
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=3.2.0 <4.13.3-r2
- Alpine:v3.12: `xen` — affected >=3.2.0 <4.13.3-r2
- Alpine:v3.13: `xen` — affected >=3.2.0 <4.14.2-r0
- Alpine:v3.14: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.15: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.16: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.17: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.18: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.19: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.20: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.21: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.22: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.23: `xen` — affected >=3.2.0 <4.15.0-r2
- Alpine:v3.24: `xen` — affected >=3.2.0 <4.15.0-r2

## Details
long running loops in grant table handling In order to properly monitor resource use, Xen maintains information on the grant mappings a domain may create to map grants offered by other domains. In the process of carrying out certain actions, Xen would iterate over all such entries, including ones which aren't in use anymore and some which may have been created but never used. If the number of entries for a given domain is large enough, this iterating of the entire table may tie up a CPU for too long, starving other domains or causing issues in the hypervisor itself. Note that a domain may map its own grants, i.e. there is no need for multiple domains to be involved here. A pair of "cooperating" guests may, however, cause the effects to be more severe.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28698
