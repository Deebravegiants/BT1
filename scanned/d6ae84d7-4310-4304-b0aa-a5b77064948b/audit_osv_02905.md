# [M] ALPINE-CVE-2023-46839

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-46839
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46839
Type: osv

## Affected
- Alpine:v3.16: `xen` — affected >=0 <4.16.5-r6
- Alpine:v3.17: `xen` — affected >=0 <4.16.5-r6
- Alpine:v3.18: `xen` — affected >=0 <4.17.3-r0
- Alpine:v3.19: `xen` — affected >=0 <4.18.0-r3
- Alpine:v3.20: `xen` — affected >=0 <4.18.0-r3
- Alpine:v3.21: `xen` — affected >=0 <4.18.0-r3
- Alpine:v3.22: `xen` — affected >=0 <4.18.0-r3
- Alpine:v3.23: `xen` — affected >=0 <4.18.0-r3
- Alpine:v3.24: `xen` — affected >=0 <4.18.0-r3

## Details
PCI devices can make use of a functionality called phantom functions,
that when enabled allows the device to generate requests using the IDs
of functions that are otherwise unpopulated.  This allows a device to
extend the number of outstanding requests.

Such phantom functions need an IOMMU context setup, but failure to
setup the context is not fatal when the device is assigned.  Not
failing device assignment when such failure happens can lead to the
primary device being assigned to a guest, while some of the phantom
functions are assigned to a different domain.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46839
