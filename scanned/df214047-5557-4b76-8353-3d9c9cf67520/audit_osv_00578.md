# [M] ALPINE-CVE-2017-17046

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-17046
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2017-11-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-17046
Type: osv

## Affected
- Alpine:v3.4: `xen` — affected >=0 <4.6.6-r2
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r3
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r3

## Details
An issue was discovered in Xen through 4.9.x on the ARM platform allowing guest OS users to obtain sensitive information from DRAM after a reboot, because disjoint blocks, and physical addresses that do not start at zero, are mishandled.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-17046
