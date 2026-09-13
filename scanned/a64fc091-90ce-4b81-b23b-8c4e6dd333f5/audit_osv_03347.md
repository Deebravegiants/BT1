# [H] ALPINE-CVE-2025-58149

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-58149
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-58149
Type: osv

## Affected
- Alpine:v3.19: `xen` — affected >=4.0.0 <4.18.5-r3
- Alpine:v3.20: `xen` — affected >=4.0.0 <4.18.5-r3
- Alpine:v3.21: `xen` — affected >=4.0.0 <4.19.3-r2
- Alpine:v3.22: `xen` — affected >=4.0.0 <4.20.1-r2
- Alpine:v3.23: `xen` — affected >=4.0.0 <4.20.1-r2
- Alpine:v3.24: `xen` — affected >=4.0.0 <4.20.1-r2

## Details
When passing through PCI devices, the detach logic in libxl won't remove
access permissions to any 64bit memory BARs the device might have.  As a
result a domain can still have access any 64bit memory BAR when such
device is no longer assigned to the domain.

For PV domains the permission leak allows the domain itself to map the memory
in the page-tables.  For HVM it would require a compromised device model or
stubdomain to map the leaked memory into the HVM domain p2m.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-58149
