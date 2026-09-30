# [H] ALPINE-CVE-2021-28705

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-28705
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28705
Type: osv

## Affected
- Alpine:v3.11: `xen` — affected >=3.4.0 <4.13.4-r2
- Alpine:v3.12: `xen` — affected >=3.4.0 <4.13.4-r2
- Alpine:v3.13: `xen` — affected >=3.4.0 <4.14.3-r2
- Alpine:v3.14: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.15: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.16: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.17: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.18: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.19: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.20: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.21: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.22: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.23: `xen` — affected >=3.4.0 <4.15.1-r2
- Alpine:v3.24: `xen` — affected >=3.4.0 <4.15.1-r2

## Details
issues with partially successful P2M updates on x86 T[his CNA information record relates to multiple CVEs; the text explains which aspects/vulnerabilities correspond to which CVE.] x86 HVM and PVH guests may be started in populate-on-demand (PoD) mode, to provide a way for them to later easily have more memory assigned. Guests are permitted to control certain P2M aspects of individual pages via hypercalls. These hypercalls may act on ranges of pages specified via page orders (resulting in a power-of-2 number of pages). In some cases the hypervisor carries out the requests by splitting them into smaller chunks. Error handling in certain PoD cases has been insufficient in that in particular partial success of some operations was not properly accounted for. There are two code paths affected - page removal (CVE-2021-28705) and insertion of new pages (CVE-2021-28709). (We provide one patch which combines the fix to both issues.)

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28705
