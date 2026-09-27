# [M] ALPINE-CVE-2017-12855

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-12855
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-08-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12855
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.11: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.12: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.13: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.14: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.15: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.16: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.17: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.18: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.19: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.20: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.21: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.22: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.23: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.24: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.3: `xen` — affected >=0 <4.6.6-r0
- Alpine:v3.4: `xen` — affected >=0 <4.6.6-r0
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r0
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r0
- Alpine:v3.7: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.8: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.9: `xen` — affected >=0 <4.9.0-r1

## Details
Xen maintains the _GTF_{read,writ}ing bits as appropriate, to inform the guest that a grant is in use. A guest is expected not to modify the grant details while it is in use, whereas the guest is free to modify/reuse the grant entry when it is not in use. Under some circumstances, Xen will clear the status bits too early, incorrectly informing the guest that the grant is no longer in use. A guest may prematurely believe that a granted frame is safely private again, and reuse it in a way which contains sensitive information, while the domain on the far end of the grant is still using the grant. Xen 4.9, 4.8, 4.7, 4.6, and 4.5 are affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12855
