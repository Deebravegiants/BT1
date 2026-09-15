# [C] ALPINE-CVE-2017-10921

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-10921
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 10.0 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-07-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-10921
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.11: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.12: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.13: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.14: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.15: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.16: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.17: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.18: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.3: `xen` — affected >=0 <4.6.6-r0
- Alpine:v3.4: `xen` — affected >=0 <4.6.6-r0
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r0
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r0
- Alpine:v3.7: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.8: `xen` — affected >=0 <4.9.0-r0
- Alpine:v3.9: `xen` — affected >=0 <4.9.0-r0

## Details
The grant-table feature in Xen through 4.8.x does not ensure sufficient type counts for a GNTMAP_device_map and GNTMAP_host_map mapping, which allows guest OS users to cause a denial of service (count mismanagement and memory corruption) or obtain privileged host OS access, aka XSA-224 bug 2.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-10921
